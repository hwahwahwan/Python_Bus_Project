"""
API 설정 모듈

이 모듈은 외부 API 관련 설정 및 환경변수를 관리합니다.
"""

import os
from dotenv import load_dotenv

from src.utils.constants import BUS_API_URL

# 환경변수 로드
load_dotenv()


def get_bus_api_key() -> str:
    """
    서울시 버스 API 키를 반환합니다.

    Returns:
        str: API 키

    Raises:
        ValueError: API 키가 설정되지 않은 경우
    """
    api_key = os.getenv('DATA_PORTAL_KEY')

    if not api_key:
        raise ValueError(
            "DATA_PORTAL_KEY가 .env 파일에 설정되지 않았습니다."
        )

    return api_key


def get_bus_api_url() -> str:
    """
    서울시 버스 API 엔드포인트 URL을 반환합니다.

    Returns:
        str: API URL
    """
    return BUS_API_URL


# 모듈 레벨에서 API 키 검증 (선택적)
try:
    API_KEY = get_bus_api_key()
    API_URL = get_bus_api_url()
except ValueError:
    # API 키가 없어도 import는 가능하도록 함
    API_KEY = None
    API_URL = BUS_API_URL
