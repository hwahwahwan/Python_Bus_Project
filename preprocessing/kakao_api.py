"""
카카오 로컬 API 연동 모듈

이 모듈은 카카오 로컬 API를 사용하여 좌표를 주소로 변환하는 기능을 제공합니다.
Rate limiting과 재시도 로직을 포함하여 안정적인 API 호출을 보장합니다.
"""

import os
import time
import requests
from typing import Optional
from dotenv import load_dotenv
from utils import extract_district

# 환경변수 로드
load_dotenv()

# 카카오 API 설정
KAKAO_API_KEY = os.getenv('KAKAO_API_KEY')
KAKAO_API_URL = 'https://dapi.kakao.com/v2/local/geo/coord2address.json'

# Rate limiting 설정
REQUEST_DELAY = 0.1  # 요청 간 대기 시간 (초)
MAX_RETRIES = 3      # 최대 재시도 횟수


def coord_to_address(lat: float, lon: float, retry_count: int = 0) -> Optional[str]:
    """
    카카오 로컬 API를 사용하여 좌표를 주소로 변환하고 구 정보를 추출합니다.
    
    Args:
        lat (float): 위도
        lon (float): 경도
        retry_count (int): 현재 재시도 횟수 (내부 사용)
        
    Returns:
        Optional[str]: 추출된 구 이름 (예: "강남구"), 실패 시 None
        
    Examples:
        >>> coord_to_address(37.5665, 126.9780)
        "종로구"
    """
    if not KAKAO_API_KEY:
        print("❌ 오류: KAKAO_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 KAKAO_API_KEY를 설정해주세요.")
        return None
    
    try:
        # Rate limiting: 요청 간 대기
        time.sleep(REQUEST_DELAY)
        
        # API 요청
        headers = {
            'Authorization': f'KakaoAK {KAKAO_API_KEY}'
        }
        params = {
            'x': lon,  # 카카오 API는 경도(x), 위도(y) 순서
            'y': lat
        }
        
        response = requests.get(
            KAKAO_API_URL,
            headers=headers,
            params=params,
            timeout=10
        )
        
        # 응답 확인
        if response.status_code == 200:
            data = response.json()
            
            # 주소 정보 추출
            if data.get('documents') and len(data['documents']) > 0:
                # 도로명 주소 우선, 없으면 지번 주소 사용
                address_info = data['documents'][0].get('road_address')
                if not address_info:
                    address_info = data['documents'][0].get('address')
                
                if address_info:
                    # 전체 주소에서 구 정보 추출
                    full_address = address_info.get('address_name', '')
                    district = extract_district(full_address)
                    
                    if district:
                        return district
                    else:
                        print(f"⚠️  경고: 주소에서 구 정보를 추출할 수 없습니다: {full_address}")
                        return None
            
            print(f"⚠️  경고: 좌표 ({lat}, {lon})에 대한 주소 정보가 없습니다.")
            return None
        
        elif response.status_code == 429:
            # Rate limit 초과
            print(f"⚠️  Rate limit 초과. 5초 대기 후 재시도... (시도 {retry_count + 1}/{MAX_RETRIES})")
            if retry_count < MAX_RETRIES:
                time.sleep(5)
                return coord_to_address(lat, lon, retry_count + 1)
            else:
                print(f"❌ 최대 재시도 횟수 초과: ({lat}, {lon})")
                return None
        
        else:
            # 기타 오류
            print(f"❌ API 오류 (status {response.status_code}): {response.text}")
            if retry_count < MAX_RETRIES:
                print(f"   재시도 중... (시도 {retry_count + 1}/{MAX_RETRIES})")
                time.sleep(2)
                return coord_to_address(lat, lon, retry_count + 1)
            else:
                print(f"❌ 최대 재시도 횟수 초과: ({lat}, {lon})")
                return None
    
    except requests.exceptions.Timeout:
        print(f"⚠️  타임아웃 발생: ({lat}, {lon})")
        if retry_count < MAX_RETRIES:
            print(f"   재시도 중... (시도 {retry_count + 1}/{MAX_RETRIES})")
            time.sleep(2)
            return coord_to_address(lat, lon, retry_count + 1)
        else:
            print(f"❌ 최대 재시도 횟수 초과: ({lat}, {lon})")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"❌ 네트워크 오류: {e}")
        if retry_count < MAX_RETRIES:
            print(f"   재시도 중... (시도 {retry_count + 1}/{MAX_RETRIES})")
            time.sleep(2)
            return coord_to_address(lat, lon, retry_count + 1)
        else:
            print(f"❌ 최대 재시도 횟수 초과: ({lat}, {lon})")
            return None
    
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return None


def test_api_connection() -> bool:
    """
    카카오 API 연결을 테스트합니다.
    
    Returns:
        bool: 연결 성공 시 True, 실패 시 False
    """
    print("🔍 카카오 API 연결 테스트 중...")
    
    # 서울시청 좌표로 테스트
    test_lat = 37.5665
    test_lon = 126.9780
    
    result = coord_to_address(test_lat, test_lon)
    
    if result:
        print(f"✅ API 연결 성공! 테스트 결과: {result}")
        return True
    else:
        print("❌ API 연결 실패!")
        return False


if __name__ == "__main__":
    # 모듈 직접 실행 시 테스트
    test_api_connection()
