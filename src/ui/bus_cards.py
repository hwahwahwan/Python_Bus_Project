"""
버스 도착 정보 카드 UI 컴포넌트

이 모듈은 버스 도착 정보를 그리드 형태의 카드로 표시하는 UI를 제공합니다.
"""

import streamlit as st
from typing import List, Dict
from datetime import datetime

from src.core.session_manager import (
    get_bus_data,
    set_bus_data,
    set_last_update
)
from src.api.bus_api import get_bus_arrival_info
from src.utils.constants import (
    MAX_DISPLAY_BUSES,
    BUS_TYPE_ICONS,
    BUS_TYPE_LOW_FLOOR,
    LAST_BUS_FLAG_YES,
    LAST_BUS_ICON,
    DEFAULT_VALUE_NO_INFO,
    INFO_MSG_REFRESH_TO_VIEW,
    DATE_TIME_FORMAT
)


def get_bus_type_icon(bus_type: str) -> str:
    """
    버스 타입 코드에 해당하는 아이콘을 반환합니다.

    Args:
        bus_type: 버스 타입 코드 ('0', '1', '2')

    Returns:
        str: 버스 타입 아이콘
    """
    return BUS_TYPE_ICONS.get(bus_type, "🔵 일반")


def render_bus_card(bus: Dict[str, str], col) -> None:
    """
    개별 버스 정보 카드를 렌더링합니다.

    Args:
        bus: 버스 정보 딕셔너리
        col: Streamlit 컬럼 객체
    """
    with col:
        # 버스 번호
        bus_no = bus.get('rtNm', DEFAULT_VALUE_NO_INFO)
        direction = bus.get('stNm', '')

        # 도착 정보
        first_arrival = bus.get('arrmsg1', DEFAULT_VALUE_NO_INFO)
        second_arrival = bus.get('arrmsg2', DEFAULT_VALUE_NO_INFO)

        # 버스 타입 (첫 번째 버스 기준) - 저상버스만 표시
        bus_type1 = bus.get('busType1', '0')
        bus_type_badge = ""
        if bus_type1 == BUS_TYPE_LOW_FLOOR:
            bus_type_badge = '<span style="background-color: #4CAF50; color: white; padding: 6px 12px; border-radius: 15px; font-size: 0.85em; font-weight: 600; margin-left: 8px;">저상</span>'

        # 막차 여부
        is_last = LAST_BUS_ICON if bus.get('nextBus') == LAST_BUS_FLAG_YES else ""

        # 카드 HTML 생성 (한 줄로 압축) - 첫 번째 버스는 파란색(#2196F3)으로 표시
        card_html = f'<div style="padding: 18px; border-radius: 12px; border: 1px solid #e0e0e0; background-color: white; box-shadow: 0 1px 4px rgba(0,0,0,0.08); margin-bottom: 12px;"><div style="display: flex; align-items: center; margin-bottom: 12px;"><span style="background-color: #2196F3; color: white; padding: 6px 14px; border-radius: 18px; font-weight: bold; font-size: 1em;">{bus_no}</span>{bus_type_badge}<span style="margin-left: auto; font-size: 0.9em;">{is_last}</span></div><p style="color: #666; font-size: 0.9em; margin: 8px 0;">{direction if direction else "방면 정보 없음"}</p><hr style="border: none; border-top: 1px solid #eee; margin: 12px 0;"><div style="margin-top: 12px;"><div style="margin-bottom: 8px;"><span style="color: #888; font-size: 0.8em;">첫 번째 버스</span><div style="font-size: 1em; font-weight: 600; color: #2196F3; margin-top: 4px;">{first_arrival}</div></div><div><span style="color: #888; font-size: 0.8em;">두 번째 버스</span><div style="font-size: 1em; font-weight: 600; color: #333; margin-top: 4px;">{second_arrival if second_arrival != DEFAULT_VALUE_NO_INFO else "정보없음"}</div></div></div></div>'

        st.markdown(card_html, unsafe_allow_html=True)


def calculate_grid_layout(num_buses: int) -> int:
    """
    버스 개수에 따라 최적의 그리드 컬럼 수를 계산합니다.

    Args:
        num_buses: 표시할 버스 개수

    Returns:
        int: 컬럼 수
    """
    if num_buses == 1:
        return 1
    elif num_buses == 2:
        return 2
    elif num_buses == 3:
        return 3
    else:
        return 4


def render_bus_arrival_section(ars_id: str) -> None:
    """
    버스 도착 정보 섹션을 렌더링합니다.

    Args:
        ars_id: 정류소 ARS-ID
    """
    st.divider()

    # 새로고침 버튼 (헤더와 같은 줄)
    col_title, col_refresh = st.columns([4, 1])

    with col_title:
        st.subheader("🚏 도착 예정 버스")

    # 자동 조회 체크 (정류장 선택 시)
    auto_refresh = st.session_state.get('auto_refresh', False)

    with col_refresh:
        manual_refresh = st.button("🔄 새로고침", width="stretch")

    # 수동 새로고침 또는 자동 조회
    if manual_refresh or auto_refresh:
        with st.spinner("버스 정보 조회 중..."):
            result = get_bus_arrival_info(ars_id)
            set_bus_data(result)
            set_last_update(datetime.now())
            # 자동 조회 플래그 초기화
            if auto_refresh:
                st.session_state['auto_refresh'] = False

    # 마지막 업데이트 시간 표시
    from src.core.session_manager import get_last_update
    last_update = get_last_update()

    if last_update:
        update_time_str = last_update.strftime(DATE_TIME_FORMAT)
        st.caption(f"⏰ 마지막 업데이트: {update_time_str}")

    # 버스 정보 표시
    bus_data = get_bus_data()

    if not bus_data:
        st.info(INFO_MSG_REFRESH_TO_VIEW)
        return

    # 에러 처리
    if bus_data.get('error'):
        st.error(bus_data['message'])
        return

    # 도착 버스 없음
    bus_list = bus_data.get('data', [])

    if len(bus_list) == 0:
        st.warning(bus_data.get('message', '현재 도착 예정 버스가 없습니다.'))
        return

    # 버스 카드 그리드 생성
    num_buses = min(len(bus_list), MAX_DISPLAY_BUSES)
    num_cols = calculate_grid_layout(num_buses)

    cols = st.columns(num_cols)

    # 각 버스 카드 렌더링
    for idx, bus in enumerate(bus_list[:MAX_DISPLAY_BUSES]):
        render_bus_card(bus, cols[idx % num_cols])
