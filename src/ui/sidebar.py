"""
사이드바 UI 컴포넌트

이 모듈은 왼쪽 사이드바의 정류장 검색 및 선택 UI를 제공합니다.
"""

import streamlit as st
import pandas as pd
from typing import Optional

from src.core.data_loader import (
    get_region_list,
    filter_by_region,
    filter_by_search,
    get_stop_by_display_name
)
from src.core.session_manager import (
    check_and_reset_on_region_change,
    set_target_stop,
    get_target_stop
)
from src.utils.constants import (
    WARNING_MSG_NO_SEARCH_RESULT,
    SUCCESS_MSG_TEMPLATE
)


def render_sidebar(df: pd.DataFrame) -> Optional[pd.Series]:
    """
    사이드바를 렌더링하고 사용자 선택을 처리합니다.

    Args:
        df: 전체 정류소 데이터

    Returns:
        Optional[pd.Series]: 선택된 정류장 정보 또는 None
    """
    with st.sidebar:
        st.header("🔎 검색")

        # STEP 1: 지역 선택
        region_list = get_region_list(df)
        selected_region = st.selectbox(
            "지역 선택",
            region_list,
            key='region_select'
        )

        # 지역 변경 감지 → 세션 초기화
        check_and_reset_on_region_change(selected_region)

        # 지역으로 필터링
        filtered_df = filter_by_region(df, selected_region)

        # STEP 2: 검색 (하이브리드 필터링)
        search_text = st.text_input(
            "🔍 정류장명 검색",
            placeholder="예: 논현",
            key='search_input'
        )

        # 검색 필터링
        search_filtered_df = filter_by_search(filtered_df, search_text)

        # 검색 결과 없음 처리
        if search_filtered_df.empty:
            st.warning(WARNING_MSG_NO_SEARCH_RESULT)
            return None

        # STEP 3: 정류장 선택
        stop_list = search_filtered_df['display_name'].tolist()
        selected_stop_name = st.selectbox(
            "정류장 선택",
            stop_list,
            key='stop_select'
        )

        # 선택된 정류장 데이터 추출
        target_stop = get_stop_by_display_name(
            search_filtered_df,
            selected_stop_name
        )

        if target_stop is None:
            st.error(f"데이터 매칭 실패: {selected_stop_name}")
            return None

        # 정류장 변경 감지 (자동 API 호출을 위해)
        prev_stop = get_target_stop()
        stop_changed = (
            prev_stop is None or
            prev_stop['ars_id'] != target_stop['ars_id']
        )

        # 세션에 저장
        set_target_stop(target_stop)

        # 정류장이 변경되면 자동으로 버스 정보 조회
        if stop_changed:
            st.session_state['auto_refresh'] = True

        # STEP 4: 선택 피드백
        success_message = SUCCESS_MSG_TEMPLATE.format(
            station_name=target_stop['station_name'],
            ars_id=target_stop['ars_id']
        )
        st.success(success_message)

        # 키보드 네비게이션 안내
        with st.expander("⌨️ 키보드 단축키"):
            st.markdown("""
            - **Tab**: 다음 요소로 이동
            - **Shift + Tab**: 이전 요소로 이동
            - **↑/↓**: 드롭다운 항목 이동
            - **Enter**: 선택 확정
            """)

        return target_stop
