"""
서울시 실시간 버스 대시보드

이 애플리케이션은 서울시 버스 정류장 정보와 실시간 버스 도착 정보를 제공합니다.

실행 방법:
    streamlit run app.py
"""

import streamlit as st

# 내부 모듈 임포트
from src.core.data_loader import load_stops_data
from src.core.session_manager import initialize_session_state, is_stop_selected, get_last_update
from src.ui.sidebar import render_sidebar
from src.ui.bus_cards import render_bus_arrival_section
from src.ui.map_view import render_map_section
from src.ui.bus_tracker import render_bus_tracker
from src.utils.constants import (
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT_MODE,
    INFO_MSG_SELECT_STOP
)


def configure_page() -> None:
    """페이지 설정을 구성합니다."""
    st.set_page_config(
        layout=LAYOUT_MODE,
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON
    )


def render_stop_not_selected_message() -> None:
    """정류장 미선택 시 안내 메시지를 표시합니다."""
    st.info(INFO_MSG_SELECT_STOP)


def render_stop_dashboard(target_stop) -> None:
    """
    정류장 도착정보 대시보드를 렌더링합니다.

    Args:
        target_stop: 선택된 정류장 정보
    """
    # 정류장 정보 헤더 (프로토타입 스타일 - 박스형)
    # 마지막 업데이트 시간 포맷팅
    last_update = get_last_update()
    update_time_str = ""
    if last_update:
        time_str = last_update.strftime('%p %I:%M:%S')
        # AM/PM을 한국어로 변환
        time_str = time_str.replace('AM', '오전').replace('PM', '오후')
        update_time_str = f'<br>마지막 업데이트: {time_str}'

    header_html = f'<div style="padding: 20px; border-radius: 12px; border: 1px solid #e0e0e0; background-color: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px;"><h2 style="margin: 0 0 10px 0; font-size: 1.5em; color: #333;">📍 정류장 정보</h2><p style="color: #666; font-size: 0.9em; margin: 0; line-height: 1.6;">{target_stop["station_name"]}<br>정류장 ID: {target_stop["ars_id"]}<br>위치: {target_stop["lat"]}, {target_stop["lon"]}{update_time_str}</p></div>'
    st.markdown(header_html, unsafe_allow_html=True)

    # 버스 도착 정보 섹션
    render_bus_arrival_section(target_stop['ars_id'])

    # 지도 섹션
    render_map_section(target_stop['lat'], target_stop['lon'])


def main() -> None:
    """메인 애플리케이션 엔트리 포인트"""

    # 1. 페이지 설정
    configure_page()

    # 2. 세션 상태 초기화
    initialize_session_state()

    # 3. 메인 헤더
    st.title(f"{PAGE_ICON} {PAGE_TITLE}")
    st.caption("정류장 도착정보 · 버스 실시간 위치 조회")

    # 4. 탭 네비게이션
    tab1, tab2 = st.tabs(["정류장 조회", "실시간 버스 추적"])

    with tab1:
        # 정류장 도착정보 대시보드
        try:
            df = load_stops_data()
        except Exception as e:
            st.error(f"❌ 데이터 로드 실패: {e}")
            st.info("💡 data/stops_processed.csv 파일이 존재하는지 확인해주세요.")
            st.stop()

        # 사이드바 렌더링 (정류장 선택)
        target_stop = render_sidebar(df)

        # 정류장 선택 여부에 따른 콘텐츠 표시
        if not is_stop_selected() or target_stop is None:
            render_stop_not_selected_message()
            st.stop()

        # 정류장 대시보드 렌더링
        render_stop_dashboard(target_stop)

    with tab2:
        # 버스 위치 추적 대시보드
        render_bus_tracker()


if __name__ == "__main__":
    main()
