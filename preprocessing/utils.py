"""
공통 유틸리티 함수 모듈

이 모듈은 데이터 전처리 과정에서 재사용 가능한 헬퍼 함수들을 제공합니다.
"""

import re
from typing import Optional


def pad_ars_id(ars_id: str) -> str:
    """
    ARS_ID를 5자리로 제로패딩합니다.
    
    Args:
        ars_id (str): 원본 ARS_ID
        
    Returns:
        str: 5자리로 패딩된 ARS_ID
        
    Examples:
        >>> pad_ars_id("123")
        "00123"
        >>> pad_ars_id("12345")
        "12345"
    """
    return str(ars_id).zfill(5)


def extract_district(address: str) -> Optional[str]:
    """
    주소 문자열에서 '구' 정보를 추출합니다.
    
    Args:
        address (str): 전체 주소 문자열
        
    Returns:
        Optional[str]: 추출된 구 이름 (예: "강남구"), 없으면 None
        
    Examples:
        >>> extract_district("서울특별시 강남구 역삼동")
        "강남구"
        >>> extract_district("경기도 성남시 분당구 정자동")
        "분당구"
        >>> extract_district("인천광역시 중구 운서동")
        "중구"
    """
    if not address or not isinstance(address, str):
        return None
    
    # 정규식으로 '구' 추출 (예: 강남구, 분당구, 중구 등)
    # 패턴: 한글 + '구' 형태
    match = re.search(r'([가-힣]+구)(?:\s|$)', address)
    
    if match:
        return match.group(1)
    
    return None


def create_display_name(station_name: str, ars_id: str) -> str:
    """
    정류소명과 ARS_ID를 병합하여 표시용 이름을 생성합니다.
    
    Args:
        station_name (str): 정류소명
        ars_id (str): ARS_ID (5자리)
        
    Returns:
        str: 병합된 표시명 (형식: "정류소명(ARS_ID)")
        
    Examples:
        >>> create_display_name("강남역", "23111")
        "강남역(23111)"
        >>> create_display_name("신촌역", "14979")
        "신촌역(14979)"
    """
    return f"{station_name}({ars_id})"


def is_valid_coordinate(lat: float, lon: float) -> bool:
    """
    좌표가 유효한지 검증합니다.
    
    Args:
        lat (float): 위도
        lon (float): 경도
        
    Returns:
        bool: 유효하면 True, 아니면 False
        
    Examples:
        >>> is_valid_coordinate(37.5665, 126.9780)
        True
        >>> is_valid_coordinate(0, 0)
        False
        >>> is_valid_coordinate(None, 127.0)
        False
    """
    try:
        lat = float(lat)
        lon = float(lon)
        
        # 0인 경우 무효
        if lat == 0 or lon == 0:
            return False
        
        # 위도는 -90 ~ 90, 경도는 -180 ~ 180 범위
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return False
        
        return True
    except (ValueError, TypeError):
        return False
