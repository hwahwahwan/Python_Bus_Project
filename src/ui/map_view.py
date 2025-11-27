"""
지도 뷰 UI 컴포넌트

이 모듈은 PyDeck을 사용하여 정류장 위치를 지도에 표시하는 UI를 제공합니다.
"""

import streamlit as st
import pydeck as pdk
import pandas as pd
from typing import Optional

from src.utils.constants import (
    DEFAULT_ZOOM_LEVEL,
    MAP_POINT_COLOR,
    MAP_POINT_RADIUS,
    MAP_STYLE
)


def create_map_layer(lat: float, lon: float) -> pdk.Layer:
    """
    지도 레이어를 생성합니다.

    Args:
        lat: 위도
        lon: 경도

    Returns:
        pdk.Layer: PyDeck 레이어 객체
    """
    # 데이터프레임 생성
    data = pd.DataFrame([{
        'lat': lat,
        'lon': lon
    }])

    # ScatterplotLayer 생성 (radius_min_pixels와 radius_max_pixels로 스케일 고정)
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=data,
        get_position='[lon, lat]',
        get_color=MAP_POINT_COLOR,
        get_radius=MAP_POINT_RADIUS,
        radius_min_pixels=8,  # 최소 크기 (픽셀 단위)
        radius_max_pixels=12,  # 최대 크기 (픽셀 단위)
        pickable=False  # 클릭 이벤트 없음
    )

    return layer


def create_view_state(lat: float, lon: float, zoom: int = DEFAULT_ZOOM_LEVEL) -> pdk.ViewState:
    """
    지도 뷰 상태를 생성합니다.

    Args:
        lat: 위도
        lon: 경도
        zoom: 줌 레벨

    Returns:
        pdk.ViewState: 뷰 상태 객체
    """
    return pdk.ViewState(
        latitude=lat,
        longitude=lon,
        zoom=zoom,
        pitch=0  # 2D 뷰
    )


def create_map_deck(lat: float, lon: float) -> pdk.Deck:
    """
    완전한 지도 Deck 객체를 생성합니다.

    Args:
        lat: 위도
        lon: 경도

    Returns:
        pdk.Deck: PyDeck Deck 객체
    """
    view_state = create_view_state(lat, lon)
    layer = create_map_layer(lat, lon)

    return pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style='road'  # 'road', 'satellite', 'light', 'dark' 중 선택
    )


def render_map_section(lat: float, lon: float) -> None:
    """
    지도 섹션을 렌더링합니다.

    Args:
        lat: 위도
        lon: 경도
    """
    st.divider()
    st.subheader("🗺️ 정류장 위치")

    try:
        map_deck = create_map_deck(lat, lon)
        # 높이를 명시적으로 지정 (500px)
        st.pydeck_chart(map_deck, height=500)
    except Exception as e:
        st.error(f"❌ 지도 로드 실패: {e}")
        st.info("💡 PyDeck이 설치되어 있는지 확인해주세요: pip install pydeck")
