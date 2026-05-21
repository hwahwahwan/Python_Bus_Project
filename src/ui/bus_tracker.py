"""
버스 추적 UI 모듈

이 모듈은 실시간 버스 위치 추적 UI를 제공합니다.
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import time
from typing import List, Dict, Optional

from src.core.data_loader import (
    get_route_list,
    get_route_data,
    get_route_id_by_number,
    get_routes_by_stop_ars_id
)
from src.core.session_manager import (
    initialize_bus_tracking_state,
    get_selected_route,
    set_selected_route,
    get_bus_positions,
    set_bus_positions,
    is_auto_refresh_enabled,
    toggle_auto_refresh,
    should_call_api,
    update_last_api_call,
    get_target_stop,
    get_bus_position_state,
    update_bus_position_state,
    get_elapsed_time_since_fetch,
    get_map_view_state,
    set_map_view_state,
    reset_map_view_state
)
from src.api.bus_api import get_bus_positions as fetch_bus_positions
from src.ui.map_view import create_bus_tracking_map
from src.utils.constants import AUTO_REFRESH_INTERVAL_SECONDS, ANIMATION_INTERVAL_SECONDS


def render_bus_tracker() -> None:
    """버스 추적 메인 화면을 렌더링합니다."""
    initialize_bus_tracking_state()

    # 메인 콘텐츠
    selected_route = get_selected_route()

    if not selected_route:
        st.info("👈 '정류장 조회' 탭에서 버스 카드의 '🔍 추적' 버튼을 눌러 노선을 선택해주세요.")
        return

    # 노선 정보 박스
    # 세션에서 route_id 가져오기 (버스 카드에서 저장한 값)
    route_id = st.session_state.get('selected_route_id')
    if not route_id:
        # 없으면 노선 번호로 조회 시도 (하위 호환성)
        route_id = get_route_id_by_number(selected_route)

    bus_positions = get_bus_positions()
    _render_route_info_box(selected_route, route_id or "N/A", len(bus_positions))

    # 수동 새로고침 + 자동 새로고침 버튼
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 새로고침", key="refresh_bus_positions", use_container_width=True):
            _fetch_and_update_bus_positions(selected_route)
            st.rerun()

    with col2:
        current_state = is_auto_refresh_enabled()
        button_text = "⏸️ 자동 새로고침 끄기" if current_state else "▶️ 자동 새로고침 켜기"

        if st.button(button_text, key="toggle_auto_refresh", use_container_width=True):
            toggle_auto_refresh()
            st.rerun()

    # 자동 새로고침 상태 표시 및 처리
    if is_auto_refresh_enabled():
        st.caption(f"🔄 {AUTO_REFRESH_INTERVAL_SECONDS}초마다 자동 새로고침 (0.5초 간격 애니메이션)")

        # API 호출 시간 체크 (60초마다만)
        elapsed = get_elapsed_time_since_fetch(selected_route)

        if elapsed is None or elapsed >= AUTO_REFRESH_INTERVAL_SECONDS:
            # 60초 경과 → API 호출
            _fetch_and_update_bus_positions(selected_route)

    # 지도
    _render_map_section(selected_route)

    # 운행 차량 테이블
    _render_vehicle_table(selected_route)

    # 자동 새로고침이 켜져있으면 0.5초마다 rerun (애니메이션)
    if is_auto_refresh_enabled():
        time.sleep(ANIMATION_INTERVAL_SECONDS)  # 0.5초 대기
        st.rerun()


def _render_route_info_box(route_no: str, route_id: str, bus_count: int) -> None:
    """노선 정보 박스를 HTML로 렌더링합니다."""
    info_html = f"""
    <div style="
        background: white;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 5px solid #ff4b4b;
    ">
        <div style="font-size: 1.2rem; font-weight: bold; color: #333; border-bottom: 1px solid #eee; padding-bottom: 8px; margin-bottom: 10px;">
            버스 실시간 위치
        </div>
        <div style="display: flex; align-items: center; font-size: 1rem; margin: 5px 0;">
            <span style="width: 120px; color: #666; font-weight: 600;">노선:</span>
            <span style="color: #333; font-weight: bold;">{route_no}</span>
        </div>
        <div style="display: flex; align-items: center; font-size: 1rem; margin: 5px 0;">
            <span style="width: 120px; color: #666; font-weight: 600;">노선 ID:</span>
            <span style="color: #333; font-weight: bold;">{route_id}</span>
        </div>
        <div style="display: flex; align-items: center; font-size: 1rem; margin: 5px 0;">
            <span style="width: 120px; color: #666; font-weight: 600;">운행 중인 버스:</span>
            <span style="color: #333; font-weight: bold;">{bus_count}대</span>
        </div>
    </div>
    """
    st.markdown(info_html, unsafe_allow_html=True)


def _interpolate_positions(
    curr_positions: Optional[List[Dict]],
    prev_positions: Optional[List[Dict]],
    elapsed_sec: float,
    interval_sec: float = AUTO_REFRESH_INTERVAL_SECONDS
) -> List[Dict]:
    """
    이전 위치와 현재 위치를 선형 보간합니다.

    Args:
        curr_positions: 현재 버스 위치 리스트
        prev_positions: 이전 버스 위치 리스트
        elapsed_sec: 경과 시간(초)
        interval_sec: API 호출 간격(초)

    Returns:
        List[Dict]: 보간된 버스 위치 리스트
    """
    if not curr_positions:
        return []

    if not prev_positions:
        return curr_positions

    # 진행률 계산 (0.0 ~ 1.0)
    f = min(max(elapsed_sec / interval_sec, 0.0), 1.0)

    # DataFrame으로 변환
    curr_df = pd.DataFrame(curr_positions)
    prev_df = pd.DataFrame(prev_positions)

    # vehicle_no를 키로 이전 위치 인덱싱
    prev_idx = prev_df.set_index("vehicle_no", drop=False)

    interpolated = []
    for _, row in curr_df.iterrows():
        veh_no = row.get("vehicle_no")

        # 이전 위치에 해당 차량이 없으면 현재 위치 그대로 사용
        if pd.isna(veh_no) or veh_no not in prev_idx.index:
            interpolated.append(row.to_dict())
            continue

        prev_row = prev_idx.loc[veh_no]
        if isinstance(prev_row, pd.DataFrame):
            prev_row = prev_row.iloc[0]

        # 좌표가 유효하지 않으면 현재 위치 그대로 사용
        if (
            pd.isna(row.get("lat")) or pd.isna(row.get("lon"))
            or pd.isna(prev_row.get("lat")) or pd.isna(prev_row.get("lon"))
        ):
            interpolated.append(row.to_dict())
            continue

        # 선형 보간
        new_row = row.to_dict()
        new_row["lat"] = prev_row["lat"] + (row["lat"] - prev_row["lat"]) * f
        new_row["lon"] = prev_row["lon"] + (row["lon"] - prev_row["lon"]) * f
        interpolated.append(new_row)

    return interpolated


def _fetch_and_update_bus_positions(route_no: str) -> None:
    """버스 위치 정보를 API에서 가져와 세션에 저장합니다 (상태 업데이트 포함)."""
    # 세션에서 route_id 가져오기 (버스 카드에서 저장한 값)
    route_id = st.session_state.get('selected_route_id')
    if not route_id:
        # 없으면 노선 번호로 조회 시도 (하위 호환성)
        route_id = get_route_id_by_number(route_no)

    if not route_id:
        st.error("❌ 노선 ID를 찾을 수 없습니다.")
        return

    with st.spinner("🚌 버스 위치 정보 조회 중..."):
        result = fetch_bus_positions(route_id)

    if result["success"]:
        # 기존 세션 상태 업데이트 (하위 호환성)
        set_bus_positions(result["data"])
        update_last_api_call()

        # 새로운 상태 업데이트 (보간용)
        update_bus_position_state(route_no, result["data"])

        st.success(f"✅ {len(result['data'])}대의 버스 위치 업데이트 완료")
    else:
        st.error(result.get("error_message", "알 수 없는 오류"))


def _render_map_section(route_no: str) -> None:
    """지도 섹션을 렌더링합니다 (뷰 상태 보존 + 보간된 위치 사용)."""
    st.subheader("🗺️ 지도")

    route_data = get_route_data(route_no)

    # 상태에서 버스 위치 가져오기
    state = get_bus_position_state(route_no)
    curr_positions = state.get("curr")
    prev_positions = state.get("prev")

    # 경과 시간 계산
    elapsed = get_elapsed_time_since_fetch(route_no)

    # 보간된 위치 계산
    if curr_positions is not None and not curr_positions.empty:
        # DataFrame을 리스트로 변환
        curr_list = curr_positions.to_dict('records') if isinstance(curr_positions, pd.DataFrame) else curr_positions
        prev_list = prev_positions.to_dict('records') if isinstance(prev_positions, pd.DataFrame) and prev_positions is not None else None

        interpolated_positions = _interpolate_positions(
            curr_list,
            prev_list,
            elapsed or 0
        )
    else:
        interpolated_positions = []

    if route_data.empty:
        st.warning("⚠️ 노선 데이터가 없습니다.")
        return

    # 지도 뷰 상태 가져오기 또는 초기화
    view_state_data = get_map_view_state(route_no)

    if view_state_data is None and not route_data.empty:
        # 초기 뷰 상태: 노선 중심점
        center_lat = route_data['lat'].mean()
        center_lon = route_data['lon'].mean()
        zoom = 13
        set_map_view_state(route_no, center_lat, center_lon, zoom)
        view_state_data = {"lat": center_lat, "lon": center_lon, "zoom": zoom}

    # PyDeck 지도 생성 (뷰 상태 적용)
    deck = create_bus_tracking_map(
        route_data,
        interpolated_positions,
        view_state=view_state_data
    )
    st.pydeck_chart(deck, height=500)


def _render_vehicle_table(route_no: str) -> None:
    """운행 차량 테이블을 렌더링합니다 (보간된 위치 사용)."""
    # 상태에서 버스 위치 가져오기
    state = get_bus_position_state(route_no)
    curr_positions = state.get("curr")
    prev_positions = state.get("prev")

    # 경과 시간 계산
    elapsed = get_elapsed_time_since_fetch(route_no)

    # 보간된 위치 계산
    if curr_positions is not None and not curr_positions.empty:
        curr_list = curr_positions.to_dict('records') if isinstance(curr_positions, pd.DataFrame) else curr_positions
        prev_list = prev_positions.to_dict('records') if isinstance(prev_positions, pd.DataFrame) and prev_positions is not None else None

        bus_positions = _interpolate_positions(
            curr_list,
            prev_list,
            elapsed or 0
        )
    else:
        bus_positions = []

    if not bus_positions:
        st.info("ℹ️ 운행 중인 버스가 없습니다.")
        return

    st.subheader("🚍 운행 차량 목록")

    # DataFrame 생성
    df_data = []
    for idx, bus in enumerate(bus_positions, start=1):
        bus_type = "🟢 저상" if bus.get("bus_type") == "1" else "🔵 일반"

        df_data.append({
            "순번": idx,
            "차량번호": bus.get('vehicle_no', 'N/A'),
            "유형": bus_type,
            "현재 위치": f"{bus.get('station_seq', 0)}번째 정류장",
            "혼잡도": bus.get('congestion', '정보없음'),
            "위도": f"{bus.get('lat', 0):.6f}",
            "경도": f"{bus.get('lon', 0):.6f}"
        })

    df = pd.DataFrame(df_data)

    # 스타일링된 DataFrame 표시
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "순번": st.column_config.NumberColumn("순번", width="small"),
            "차량번호": st.column_config.TextColumn("차량번호", width="medium"),
            "유형": st.column_config.TextColumn("유형", width="small"),
            "현재 위치": st.column_config.TextColumn("현재 위치", width="medium"),
            "혼잡도": st.column_config.TextColumn("혼잡도", width="small"),
            "위도": st.column_config.TextColumn("위도", width="medium"),
            "경도": st.column_config.TextColumn("경도", width="medium"),
        }
    )
