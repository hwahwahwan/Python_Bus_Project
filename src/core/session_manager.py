"""
세션 상태 관리 모듈

이 모듈은 Streamlit 세션 상태를 관리하고
사용자 선택 데이터의 수명 주기를 제어합니다.
"""

import streamlit as st
from typing import Optional, Any, List, Dict
from datetime import datetime
import time

from src.utils.constants import (
    SESSION_KEY_TARGET_STOP,
    SESSION_KEY_LAST_UPDATE,
    SESSION_KEY_PREV_REGION,
    SESSION_KEY_BUS_DATA,
    SESSION_KEY_SELECTED_ROUTE,
    SESSION_KEY_BUS_POSITIONS,
    SESSION_KEY_AUTO_REFRESH_ENABLED,
    SESSION_KEY_LAST_API_CALL,
    SESSION_KEY_ROUTE_DATA,
    AUTO_REFRESH_INTERVAL_SECONDS
)


def initialize_session_state() -> None:
    """
    세션 상태를 초기화합니다.

    앱 시작 시 한 번만 실행되며, 필요한 세션 변수들을
    None 또는 기본값으로 초기화합니다.
    """
    if SESSION_KEY_TARGET_STOP not in st.session_state:
        st.session_state[SESSION_KEY_TARGET_STOP] = None

    if SESSION_KEY_LAST_UPDATE not in st.session_state:
        st.session_state[SESSION_KEY_LAST_UPDATE] = None

    if SESSION_KEY_PREV_REGION not in st.session_state:
        st.session_state[SESSION_KEY_PREV_REGION] = None

    if SESSION_KEY_BUS_DATA not in st.session_state:
        st.session_state[SESSION_KEY_BUS_DATA] = None


def get_target_stop() -> Optional[Any]:
    """
    현재 선택된 정류장 정보를 반환합니다.

    Returns:
        Optional[Any]: 선택된 정류장 정보 (pandas.Series) 또는 None
    """
    return st.session_state.get(SESSION_KEY_TARGET_STOP)


def set_target_stop(stop_data: Any) -> None:
    """
    선택된 정류장 정보를 저장합니다.

    Args:
        stop_data: 정류장 정보 (pandas.Series)
    """
    st.session_state[SESSION_KEY_TARGET_STOP] = stop_data


def get_last_update() -> Optional[datetime]:
    """
    마지막 API 호출 시간을 반환합니다.

    Returns:
        Optional[datetime]: 마지막 업데이트 시간 또는 None
    """
    return st.session_state.get(SESSION_KEY_LAST_UPDATE)


def set_last_update(update_time: datetime) -> None:
    """
    API 호출 시간을 저장합니다.

    Args:
        update_time: 업데이트 시간
    """
    st.session_state[SESSION_KEY_LAST_UPDATE] = update_time


def get_bus_data() -> Optional[dict]:
    """
    저장된 버스 도착 정보를 반환합니다.

    Returns:
        Optional[dict]: 버스 데이터 또는 None
    """
    return st.session_state.get(SESSION_KEY_BUS_DATA)


def set_bus_data(bus_data: dict) -> None:
    """
    버스 도착 정보를 저장합니다.

    Args:
        bus_data: API 응답 데이터
    """
    st.session_state[SESSION_KEY_BUS_DATA] = bus_data


def check_and_reset_on_region_change(current_region: str) -> bool:
    """
    지역이 변경되었는지 확인하고, 변경되었다면 세션을 초기화합니다.

    Args:
        current_region: 현재 선택된 지역

    Returns:
        bool: 지역이 변경되었으면 True
    """
    prev_region = st.session_state.get(SESSION_KEY_PREV_REGION)

    if prev_region != current_region:
        # 지역이 변경됨 → 이전 정보 초기화
        st.session_state[SESSION_KEY_TARGET_STOP] = None
        st.session_state[SESSION_KEY_LAST_UPDATE] = None
        st.session_state[SESSION_KEY_BUS_DATA] = None
        st.session_state[SESSION_KEY_PREV_REGION] = current_region
        return True

    return False


def is_stop_selected() -> bool:
    """
    정류장이 선택되었는지 확인합니다.

    Returns:
        bool: 정류장이 선택되었으면 True
    """
    return st.session_state.get(SESSION_KEY_TARGET_STOP) is not None


def clear_all_session_data() -> None:
    """
    모든 세션 데이터를 초기화합니다.

    (디버그 또는 로그아웃 기능에 사용)
    """
    st.session_state[SESSION_KEY_TARGET_STOP] = None
    st.session_state[SESSION_KEY_LAST_UPDATE] = None
    st.session_state[SESSION_KEY_PREV_REGION] = None
    st.session_state[SESSION_KEY_BUS_DATA] = None


# ============================================================================
# 버스 추적 세션 관리 (버스 위치 추적용)
# ============================================================================

def initialize_bus_tracking_state() -> None:
    """
    버스 추적 기능의 세션 상태를 초기화합니다.
    """
    if SESSION_KEY_SELECTED_ROUTE not in st.session_state:
        st.session_state[SESSION_KEY_SELECTED_ROUTE] = None

    if SESSION_KEY_BUS_POSITIONS not in st.session_state:
        st.session_state[SESSION_KEY_BUS_POSITIONS] = []

    if SESSION_KEY_AUTO_REFRESH_ENABLED not in st.session_state:
        st.session_state[SESSION_KEY_AUTO_REFRESH_ENABLED] = False

    if SESSION_KEY_LAST_API_CALL not in st.session_state:
        st.session_state[SESSION_KEY_LAST_API_CALL] = None

    if SESSION_KEY_ROUTE_DATA not in st.session_state:
        st.session_state[SESSION_KEY_ROUTE_DATA] = None


def get_selected_route() -> Optional[str]:
    """
    현재 선택된 노선 번호를 반환합니다.

    Returns:
        Optional[str]: 노선 번호 또는 None
    """
    return st.session_state.get(SESSION_KEY_SELECTED_ROUTE)


def set_selected_route(route_no: str) -> None:
    """
    선택된 노선을 저장하고 관련 상태를 초기화합니다.

    Args:
        route_no: 버스 노선 번호
    """
    st.session_state[SESSION_KEY_SELECTED_ROUTE] = route_no
    st.session_state[SESSION_KEY_BUS_POSITIONS] = []
    st.session_state[SESSION_KEY_LAST_API_CALL] = None


def get_bus_positions() -> List[Dict]:
    """
    캐시된 버스 위치 정보를 반환합니다.

    Returns:
        List[Dict]: 버스 위치 목록
    """
    return st.session_state.get(SESSION_KEY_BUS_POSITIONS, [])


def set_bus_positions(positions: List[Dict]) -> None:
    """
    버스 위치 정보를 캐시합니다.

    Args:
        positions: 버스 위치 데이터 리스트
    """
    st.session_state[SESSION_KEY_BUS_POSITIONS] = positions


def is_auto_refresh_enabled() -> bool:
    """
    자동 새로고침이 활성화되었는지 확인합니다.

    Returns:
        bool: 활성화 여부
    """
    return st.session_state.get(SESSION_KEY_AUTO_REFRESH_ENABLED, False)


def toggle_auto_refresh() -> None:
    """
    자동 새로고침 상태를 토글합니다.
    """
    current = st.session_state.get(SESSION_KEY_AUTO_REFRESH_ENABLED, False)
    st.session_state[SESSION_KEY_AUTO_REFRESH_ENABLED] = not current


def should_call_api() -> bool:
    """
    마지막 API 호출 시간을 기준으로 API를 호출해야 하는지 판단합니다.

    Returns:
        bool: 30초가 지났으면 True, 아니면 False
    """
    last_call = st.session_state.get(SESSION_KEY_LAST_API_CALL)

    if last_call is None:
        return True

    elapsed = time.time() - last_call
    return elapsed >= AUTO_REFRESH_INTERVAL_SECONDS


def update_last_api_call() -> None:
    """
    마지막 API 호출 시간을 현재 시간으로 업데이트합니다.
    """
    st.session_state[SESSION_KEY_LAST_API_CALL] = time.time()


# ============================================================================
# 버스 위치 애니메이션 관련 세션 관리 (보간용)
# ============================================================================

def get_bus_position_state(route_no: str) -> Dict:
    """
    노선별 버스 위치 상태를 반환합니다.

    Args:
        route_no: 노선 번호

    Returns:
        Dict: {"prev": pd.DataFrame, "curr": pd.DataFrame, "last_fetch": datetime}
    """
    state_key = f"buspos_state_{route_no}"
    if state_key not in st.session_state:
        st.session_state[state_key] = {
            "prev": None,
            "curr": None,
            "last_fetch": None
        }
    return st.session_state[state_key]


def update_bus_position_state(route_no: str, new_positions: List[Dict]) -> None:
    """
    노선별 버스 위치 상태를 업데이트합니다.

    Args:
        route_no: 노선 번호
        new_positions: 새로운 버스 위치 리스트
    """
    import pandas as pd

    state_key = f"buspos_state_{route_no}"
    state = get_bus_position_state(route_no)

    # 리스트를 DataFrame으로 변환
    new_df = pd.DataFrame(new_positions) if new_positions else None

    # 현재를 이전으로, 새 데이터를 현재로
    state["prev"] = state.get("curr")
    state["curr"] = new_df
    state["last_fetch"] = datetime.now()

    st.session_state[state_key] = state


def get_elapsed_time_since_fetch(route_no: str) -> Optional[float]:
    """
    마지막 API 호출 이후 경과 시간을 반환합니다.

    Args:
        route_no: 노선 번호

    Returns:
        Optional[float]: 경과 시간(초) 또는 None
    """
    state = get_bus_position_state(route_no)
    last_fetch = state.get("last_fetch")

    if last_fetch is None:
        return None

    return (datetime.now() - last_fetch).total_seconds()


def get_map_view_state(route_no: str) -> Optional[Dict]:
    """
    노선별 지도 뷰 상태를 반환합니다.

    Args:
        route_no: 노선 번호

    Returns:
        Optional[Dict]: {"lat": float, "lon": float, "zoom": int} 또는 None
    """
    view_key = f"bus_view_state_{route_no}"
    return st.session_state.get(view_key)


def set_map_view_state(route_no: str, lat: float, lon: float, zoom: int) -> None:
    """
    노선별 지도 뷰 상태를 저장합니다.

    Args:
        route_no: 노선 번호
        lat: 위도
        lon: 경도
        zoom: 줌 레벨
    """
    view_key = f"bus_view_state_{route_no}"
    st.session_state[view_key] = {
        "lat": lat,
        "lon": lon,
        "zoom": zoom
    }


def reset_map_view_state(route_no: str) -> None:
    """
    지도 뷰 상태를 초기화합니다 (재중심 버튼용).

    Args:
        route_no: 노선 번호
    """
    view_key = f"bus_view_state_{route_no}"
    if view_key in st.session_state:
        del st.session_state[view_key]
