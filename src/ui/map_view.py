"""
지도 뷰 UI 컴포넌트

이 모듈은 PyDeck을 사용하여 정류장 위치를 지도에 표시하는 UI를 제공합니다.
"""

import streamlit as st
import pydeck as pdk
import pandas as pd
from typing import Optional, List, Dict, Tuple

from src.utils.constants import (
    DEFAULT_ZOOM_LEVEL,
    MAP_POINT_COLOR,
    MAP_POINT_RADIUS,
    MAP_STYLE,
    ROUTE_PATH_COLOR,
    ROUTE_PATH_WIDTH,
    ROUTE_PATH_MIN_WIDTH,
    ROUTE_PATH_MAX_WIDTH,
    BUS_MARKER_COLOR,
    BUS_MARKER_RADIUS,
    CURRENT_STOP_RADIUS
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
        get_fill_color=MAP_POINT_COLOR,
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


# ============================================================================
# 버스 추적 지도 시각화 (PathLayer + ScatterplotLayer)
# ============================================================================

def calculate_bbox(coordinates: List[Tuple[float, float]]) -> Dict[str, float]:
    """
    좌표들의 Bounding Box를 계산합니다.

    Args:
        coordinates: (lat, lon) 튜플 리스트

    Returns:
        Dict: min_lat, max_lat, min_lon, max_lon
    """
    lats = [coord[0] for coord in coordinates]
    lons = [coord[1] for coord in coordinates]

    return {
        "min_lat": min(lats),
        "max_lat": max(lats),
        "min_lon": min(lons),
        "max_lon": max(lons)
    }


def calculate_centroid(coordinates: List[Tuple[float, float]]) -> Tuple[float, float]:
    """
    좌표들의 중심점을 계산합니다.

    Args:
        coordinates: (lat, lon) 튜플 리스트

    Returns:
        Tuple: (center_lat, center_lon)
    """
    lats = [coord[0] for coord in coordinates]
    lons = [coord[1] for coord in coordinates]

    return (sum(lats) / len(lats), sum(lons) / len(lons))


def calculate_zoom_level(bbox: Dict[str, float]) -> int:
    """
    Bounding Box 크기에 따라 적절한 줌 레벨을 계산합니다.

    Args:
        bbox: Bounding box 딕셔너리

    Returns:
        int: 줌 레벨 (10-16)
    """
    lat_diff = bbox["max_lat"] - bbox["min_lat"]
    lon_diff = bbox["max_lon"] - bbox["min_lon"]

    # 큰 쪽 차이를 기준으로 줌 레벨 결정
    max_diff = max(lat_diff, lon_diff)

    if max_diff > 0.5:
        return 10
    elif max_diff > 0.2:
        return 11
    elif max_diff > 0.1:
        return 12
    elif max_diff > 0.05:
        return 13
    elif max_diff > 0.02:
        return 14
    elif max_diff > 0.01:
        return 15
    else:
        return 16


def create_route_path_layer(route_data: pd.DataFrame) -> pdk.Layer:
    """
    노선 경로를 그리는 PathLayer를 생성합니다.

    Args:
        route_data: 노선 정류장 데이터 (lat, lon, station_seq 포함)

    Returns:
        pdk.Layer: PathLayer (초록색 선)
    """
    # 순번대로 정렬
    route_data = route_data.sort_values('station_seq')

    # [lon, lat] 형식의 경로 생성
    path = route_data[['lon', 'lat']].values.tolist()

    path_data = [{
        "path": path,
        "name": "bus_route"
    }]

    return pdk.Layer(
        "PathLayer",
        data=path_data,
        get_path="path",
        get_color=ROUTE_PATH_COLOR,
        width_scale=1,
        width_min_pixels=ROUTE_PATH_MIN_WIDTH,
        width_max_pixels=ROUTE_PATH_MAX_WIDTH,
        get_width=ROUTE_PATH_WIDTH,
        pickable=False
    )


def create_bus_markers_layer(bus_positions: List[Dict]) -> pdk.Layer:
    """
    버스 위치 마커 레이어를 생성합니다.

    Args:
        bus_positions: 버스 위치 데이터 리스트 (lat, lon 포함)

    Returns:
        pdk.Layer: ScatterplotLayer (빨간색 점)
    """
    return pdk.Layer(
        "ScatterplotLayer",
        data=bus_positions,
        get_position="[lon, lat]",
        get_fill_color=BUS_MARKER_COLOR,
        get_radius=BUS_MARKER_RADIUS,
        radius_scale=1,
        radius_min_pixels=8,
        radius_max_pixels=12,
        pickable=True
    )


def create_current_stop_layer(stop_data: Dict) -> pdk.Layer:
    """
    현재 선택된 정류장 마커 레이어를 생성합니다.

    Args:
        stop_data: 정류장 데이터 (lat, lon 포함)

    Returns:
        pdk.Layer: ScatterplotLayer (파란색 점)
    """
    return pdk.Layer(
        "ScatterplotLayer",
        data=[stop_data],
        get_position="[lon, lat]",
        get_fill_color=MAP_POINT_COLOR,
        get_radius=CURRENT_STOP_RADIUS,
        radius_scale=1,
        radius_min_pixels=10,
        radius_max_pixels=15,
        pickable=True
    )


def create_bus_tracking_map(
    route_data: pd.DataFrame,
    bus_positions: List[Dict],
    current_stop: Optional[Dict] = None,
    view_state: Optional[Dict] = None
) -> pdk.Deck:
    """
    버스 추적용 지도를 생성합니다 (노선 경로 + 버스 위치).

    Args:
        route_data: 노선 정류장 데이터
        bus_positions: 버스 위치 데이터 리스트
        current_stop: 선택된 정류장 (Optional)
        view_state: 지도 뷰 상태 (Optional) - {"lat": float, "lon": float, "zoom": int}

    Returns:
        pdk.Deck: 완성된 지도
    """
    # 뷰 상태 생성
    if view_state is not None:
        # 사용자 제공 뷰 상태 사용 (줌/위치 유지)
        view = pdk.ViewState(
            latitude=view_state["lat"],
            longitude=view_state["lon"],
            zoom=view_state["zoom"],
            pitch=0,
            bearing=0
        )
    else:
        # 기본 뷰 상태 (자동 계산)
        coordinates = route_data[['lat', 'lon']].values.tolist()
        coordinates = [(lat, lon) for lat, lon in coordinates]

        center_lat, center_lon = calculate_centroid(coordinates)
        bbox = calculate_bbox(coordinates)
        zoom = calculate_zoom_level(bbox)

        view = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=zoom,
            pitch=0,
            bearing=0
        )

    # 레이어 생성
    layers = [create_route_path_layer(route_data)]

    if bus_positions:
        layers.append(create_bus_markers_layer(bus_positions))

    if current_stop:
        layers.append(create_current_stop_layer(current_stop))

    # Deck 생성
    return pdk.Deck(
        layers=layers,
        initial_view_state=view,
        map_style=MAP_STYLE,
        tooltip={
            "html": "<b>{vehicle_no}</b><br/>정류장: {station_name}",
            "style": {
                "backgroundColor": "steelblue",
                "color": "white"
            }
        }
    )
