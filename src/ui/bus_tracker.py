"""
버스 추적 UI 모듈

이 모듈은 실시간 버스 위치 추적 UI를 제공합니다.
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from typing import List, Dict

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
    get_target_stop
)
from src.api.bus_api import get_bus_positions as fetch_bus_positions
from src.ui.map_view import create_bus_tracking_map
from src.utils.constants import AUTO_REFRESH_INTERVAL_SECONDS


def render_bus_tracker() -> None:
    """버스 추적 메인 화면을 렌더링합니다."""
    initialize_bus_tracking_state()

    # 사이드바
    with st.sidebar:
        st.header("🔍 노선 선택")
        _render_route_selector()

    # 메인 콘텐츠
    selected_route = get_selected_route()

    if not selected_route:
        st.info("👈 왼쪽 사이드바에서 노선을 선택해주세요.")
        return

    # 노선 정보 박스
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
        st.caption(f"🔄 {AUTO_REFRESH_INTERVAL_SECONDS}초마다 자동 새로고침")

        # API 호출 시간 체크 (60초마다만)
        if should_call_api():
            _fetch_and_update_bus_positions(selected_route)
            st.rerun()

    # 지도
    _render_map_section(selected_route)

    # 운행 차량 테이블
    _render_vehicle_table()

    # 자동 새로고침이 켜져있으면 자동으로 페이지 갱신
    # 주의: 지도 줌/위치 유지를 위해 JavaScript setTimeout 사용
    if is_auto_refresh_enabled():
        # 60초마다 자동 새로고침
        components.html(
            f"""
            <script>
                setTimeout(function() {{
                    window.parent.location.reload();
                }}, {AUTO_REFRESH_INTERVAL_SECONDS * 1000});
            </script>
            """,
            height=0
        )


def _render_route_selector() -> None:
    """노선 선택 드롭다운을 렌더링합니다."""
    try:
        # 정류장 조회 탭에서 선택된 정류장 확인
        target_stop = get_target_stop()

        # 정류장이 선택되어 있으면 해당 정류장 노선만 필터링
        if target_stop is not None and hasattr(target_stop, 'ars_id'):
            ars_id = target_stop.ars_id
            route_list = get_routes_by_stop_ars_id(ars_id)

            if not route_list:
                st.warning(f"⚠️ 선택한 정류장({target_stop.station_name})을 경유하는 노선이 없습니다.")
                st.caption("💡 모든 노선을 보려면 '정류장 조회' 탭에서 정류장 선택을 해제하세요.")
                return

            st.caption(f"📍 {target_stop.station_name} 경유 노선")
        else:
            # 정류장이 선택되지 않았으면 전체 노선 표시
            route_list = get_route_list()
            st.caption("💡 모든 버스 노선")

    except Exception as e:
        st.error(f"❌ 노선 데이터 로드 실패: {e}")
        return

    if not route_list:
        st.error("❌ 노선 데이터를 불러올 수 없습니다.")
        return

    selected = st.selectbox(
        "버스 노선",
        options=["선택하세요"] + route_list,
        key="route_selector"
    )

    if selected != "선택하세요" and selected != get_selected_route():
        set_selected_route(selected)
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


def _fetch_and_update_bus_positions(route_no: str) -> None:
    """버스 위치 정보를 API에서 가져와 세션에 저장합니다."""
    route_id = get_route_id_by_number(route_no)

    if not route_id:
        st.error("❌ 노선 ID를 찾을 수 없습니다.")
        return

    with st.spinner("🚌 버스 위치 정보 조회 중..."):
        result = fetch_bus_positions(route_id)

    if result["success"]:
        set_bus_positions(result["data"])
        update_last_api_call()
        st.success(f"✅ {len(result['data'])}대의 버스 위치 업데이트 완료")
    else:
        st.error(result.get("error_message", "알 수 없는 오류"))


def _render_map_section(route_no: str) -> None:
    """지도 섹션을 렌더링합니다."""
    st.subheader("🗺️ 지도")

    route_data = get_route_data(route_no)
    bus_positions = get_bus_positions()

    if route_data.empty:
        st.warning("⚠️ 노선 데이터가 없습니다.")
        return

    # 단일 지도 (노선 경로 + 버스 위치)
    deck = create_bus_tracking_map(route_data, bus_positions)
    st.pydeck_chart(deck, height=500)


def _render_vehicle_table() -> None:
    """운행 차량 테이블을 렌더링합니다."""
    bus_positions = get_bus_positions()

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
