"""
데이터 검증 유틸리티

이 모듈은 데이터 유효성 검사를 위한 공통 함수들을 제공합니다.
"""

from typing import Any
import pandas as pd


def is_valid_dataframe(df: Any) -> bool:
    """
    DataFrame이 유효한지 확인합니다.

    Args:
        df: 검증할 객체

    Returns:
        bool: DataFrame이 유효하고 비어있지 않으면 True
    """
    return isinstance(df, pd.DataFrame) and not df.empty


def is_valid_ars_id(ars_id: str) -> bool:
    """
    ARS ID가 유효한 형식인지 확인합니다.

    Args:
        ars_id: 검증할 ARS ID (5자리 문자열)

    Returns:
        bool: ARS ID가 유효하면 True
    """
    return (
        isinstance(ars_id, str) and
        len(ars_id) == 5 and
        ars_id.isdigit()
    )


def is_valid_coordinates(lat: float, lon: float) -> bool:
    """
    위도/경도 좌표가 유효한지 확인합니다.

    Args:
        lat: 위도
        lon: 경도

    Returns:
        bool: 좌표가 유효하면 True
    """
    try:
        lat_float = float(lat)
        lon_float = float(lon)

        # 서울 좌표 범위 체크 (대략적)
        return (
            36.0 <= lat_float <= 38.0 and
            126.0 <= lon_float <= 128.0
        )
    except (ValueError, TypeError):
        return False


def has_required_columns(df: pd.DataFrame, required_columns: list[str]) -> bool:
    """
    DataFrame이 필수 컬럼들을 포함하는지 확인합니다.

    Args:
        df: 검증할 DataFrame
        required_columns: 필수 컬럼 리스트

    Returns:
        bool: 모든 필수 컬럼이 존재하면 True
    """
    return all(col in df.columns for col in required_columns)
