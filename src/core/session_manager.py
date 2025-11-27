"""
세션 상태 관리 모듈

이 모듈은 Streamlit 세션 상태를 관리하고
사용자 선택 데이터의 수명 주기를 제어합니다.
"""

import streamlit as st
from typing import Optional, Any
from datetime import datetime

from src.utils.constants import (
    SESSION_KEY_TARGET_STOP,
    SESSION_KEY_LAST_UPDATE,
    SESSION_KEY_PREV_REGION,
    SESSION_KEY_BUS_DATA
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
