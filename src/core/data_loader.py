"""
데이터 로더 모듈

이 모듈은 CSV 데이터 로드 및 필터링 기능을 제공합니다.
Streamlit 캐싱을 활용하여 성능을 최적화합니다.
"""

import os
import streamlit as st
import pandas as pd
from typing import Optional

from src.utils.constants import (
    DATA_PATH,
    STATION_ID_DTYPE,
    ARS_ID_DTYPE,
    FIELD_REGION_NAME,
    FIELD_DISPLAY_NAME
)
from src.utils.validators import is_valid_dataframe, has_required_columns


@st.cache_data
def load_stops_data() -> pd.DataFrame:
    """
    정류소 데이터를 로드합니다.

    Streamlit의 cache_data 데코레이터를 사용하여
    불필요한 재로드를 방지합니다.

    Returns:
        pd.DataFrame: 정류소 데이터

    Raises:
        FileNotFoundError: 데이터 파일이 없을 경우
        ValueError: 데이터가 비어있거나 필수 컬럼이 없을 경우
    """
    # 파일 존재 확인
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {DATA_PATH}")

    # CSV 읽기 (ID 컬럼은 문자열로 강제)
    df = pd.read_csv(
        DATA_PATH,
        dtype={
            'station_id': STATION_ID_DTYPE,
            'ars_id': ARS_ID_DTYPE
        }
    )

    # 컬럼명 공백 제거 (데이터 정제)
    df.columns = df.columns.str.strip()

    # 유효성 검증
    if not is_valid_dataframe(df):
        raise ValueError("로드된 데이터가 비어있습니다.")

    required_columns = [
        'station_id', 'ars_id', 'station_name',
        'lat', 'lon', 'region_name', 'display_name'
    ]

    if not has_required_columns(df, required_columns):
        missing = [col for col in required_columns if col not in df.columns]
        raise ValueError(f"필수 컬럼이 누락되었습니다: {missing}")

    return df


def get_region_list(df: pd.DataFrame) -> list[str]:
    """
    구(region) 목록을 추출합니다.

    Args:
        df: 정류소 데이터프레임

    Returns:
        list[str]: 가나다순으로 정렬된 구 목록
    """
    return sorted(df[FIELD_REGION_NAME].dropna().unique().tolist())


def filter_by_region(df: pd.DataFrame, region_name: str) -> pd.DataFrame:
    """
    지역(구)으로 데이터를 필터링합니다.

    Args:
        df: 전체 정류소 데이터
        region_name: 구 이름 (예: "강남구")

    Returns:
        pd.DataFrame: 필터링된 데이터
    """
    return df[df[FIELD_REGION_NAME] == region_name].copy()


def filter_by_search(
    df: pd.DataFrame,
    search_text: Optional[str]
) -> pd.DataFrame:
    """
    검색어로 데이터를 필터링합니다.

    display_name 컬럼에서 검색어가 포함된 행만 반환합니다.
    검색어가 None이거나 빈 문자열이면 전체 데이터를 반환합니다.

    Args:
        df: 필터링할 데이터
        search_text: 검색어 (Optional)

    Returns:
        pd.DataFrame: 필터링된 데이터
    """
    if not search_text or search_text.strip() == "":
        return df

    # 대소문자 구분 없이 검색
    return df[
        df[FIELD_DISPLAY_NAME].str.contains(search_text, case=False, na=False)
    ].copy()


def get_stop_by_display_name(
    df: pd.DataFrame,
    display_name: str
) -> Optional[pd.Series]:
    """
    display_name으로 정류장 정보를 조회합니다.

    Args:
        df: 정류소 데이터
        display_name: 표시명 (예: "강남역(23111)")

    Returns:
        Optional[pd.Series]: 정류장 정보 또는 None
    """
    matches = df[df[FIELD_DISPLAY_NAME] == display_name]

    if matches.empty:
        return None

    return matches.iloc[0]
