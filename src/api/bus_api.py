"""
버스 도착 정보 API 호출 모듈

이 모듈은 서울시 공공데이터포털의 버스 도착 정보 API를 호출하고
응답을 파싱하는 기능을 제공합니다.
"""

import requests
import time
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

from src.api.api_config import API_KEY, API_URL
from src.utils.constants import (
    API_TIMEOUT_SECONDS,
    API_MAX_RETRIES,
    API_RETRY_DELAY_SECONDS,
    HTTP_OK,
    HTTP_UNAUTHORIZED,
    HTTP_FORBIDDEN,
    HTTP_NOT_FOUND,
    API_SUCCESS_CODE,
    DEFAULT_VALUE_NO_INFO,
    ERROR_MSG_NO_API_KEY,
    ERROR_MSG_AUTH_FAILED,
    ERROR_MSG_ACCESS_DENIED,
    ERROR_MSG_NOT_FOUND,
    ERROR_MSG_TIMEOUT,
    ERROR_MSG_CONNECTION,
    ERROR_MSG_MAX_RETRIES,
    ERROR_MSG_PARSE_FAILED,
    WARNING_MSG_NO_BUS,
    BUS_POSITION_API_URL
)


def parse_bus_data(item: ET.Element) -> Dict[str, str]:
    """
    XML 응답에서 버스 정보를 추출하여 딕셔너리로 변환합니다.

    Args:
        item: XML Element (itemList)

    Returns:
        Dict[str, str]: 파싱된 버스 정보
    """
    return {
        'busRouteId': item.findtext('busRouteId', ''),
        'busRouteAbrv': item.findtext('busRouteAbrv', DEFAULT_VALUE_NO_INFO),
        'rtNm': item.findtext('rtNm', DEFAULT_VALUE_NO_INFO),
        'arrmsg1': item.findtext('arrmsg1', DEFAULT_VALUE_NO_INFO),
        'arrmsg2': item.findtext('arrmsg2', DEFAULT_VALUE_NO_INFO),
        'stNm': item.findtext('stNm', ''),
        'busType1': item.findtext('busType1', '0'),
        'busType2': item.findtext('busType2', '0'),
        'routeType': item.findtext('routeType', '0'),
        'nextBus': item.findtext('nextBus', 'N'),
        'isArrive1': item.findtext('isArrive1', '0'),
        'isArrive2': item.findtext('isArrive2', '0'),
    }


def create_error_response(message: str) -> Dict[str, any]:
    """
    에러 응답 딕셔너리를 생성합니다.

    Args:
        message: 에러 메시지

    Returns:
        Dict: 에러 응답
    """
    return {
        'error': True,
        'message': message,
        'data': []
    }


def create_success_response(
    data: List[Dict],
    message: str = ""
) -> Dict[str, any]:
    """
    성공 응답 딕셔너리를 생성합니다.

    Args:
        data: 버스 정보 리스트
        message: 메시지 (선택적)

    Returns:
        Dict: 성공 응답
    """
    return {
        'error': False,
        'message': message,
        'data': data
    }


def get_bus_arrival_info(
    ars_id: str,
    max_retries: Optional[int] = None
) -> Dict[str, any]:
    """
    버스 도착 정보를 조회합니다.

    Args:
        ars_id: 정류소 ARS-ID (5자리 문자열)
        max_retries: 최대 재시도 횟수 (기본값: API_MAX_RETRIES)

    Returns:
        Dict: API 응답
            - error (bool): 에러 여부
            - message (str): 메시지
            - data (List[Dict]): 버스 정보 리스트
    """
    # API 키 확인
    if not API_KEY:
        return create_error_response(ERROR_MSG_NO_API_KEY)

    # 기본값 설정
    if max_retries is None:
        max_retries = API_MAX_RETRIES

    # API 요청 파라미터
    params = {
        'serviceKey': API_KEY,
        'arsId': ars_id
    }

    # 재시도 로직
    for attempt in range(max_retries):
        try:
            response = requests.get(
                API_URL,
                params=params,
                timeout=API_TIMEOUT_SECONDS
            )

            # HTTP 상태 코드 체크
            if response.status_code == HTTP_UNAUTHORIZED:
                return create_error_response(ERROR_MSG_AUTH_FAILED)

            elif response.status_code == HTTP_FORBIDDEN:
                return create_error_response(ERROR_MSG_ACCESS_DENIED)

            elif response.status_code == HTTP_NOT_FOUND:
                return create_error_response(ERROR_MSG_NOT_FOUND)

            elif response.status_code != HTTP_OK:
                return create_error_response(
                    f"❌ API 오류 (HTTP {response.status_code})"
                )

            # XML 파싱
            try:
                root = ET.fromstring(response.content)

                # 헤더 결과 코드 확인
                header_cd = root.findtext('.//headerCd')
                header_msg = root.findtext('.//headerMsg')

                if header_cd != API_SUCCESS_CODE:
                    return create_error_response(f"❌ API 오류: {header_msg}")

                # itemList 추출
                items = root.findall('.//itemList')

                # 도착 버스 없음
                if not items or len(items) == 0:
                    return create_success_response(
                        data=[],
                        message=WARNING_MSG_NO_BUS
                    )

                # 버스 데이터 파싱
                bus_list = [parse_bus_data(item) for item in items]

                return create_success_response(data=bus_list)

            except ET.ParseError:
                return create_error_response(ERROR_MSG_PARSE_FAILED)

        except requests.exceptions.Timeout:
            # 타임아웃 발생 → 재시도
            if attempt < max_retries - 1:
                time.sleep(API_RETRY_DELAY_SECONDS)
                continue
            return create_error_response(ERROR_MSG_TIMEOUT)

        except requests.exceptions.ConnectionError:
            return create_error_response(ERROR_MSG_CONNECTION)

        except Exception as e:
            return create_error_response(f"❌ 알 수 없는 오류: {str(e)}")

    # 최대 재시도 횟수 초과
    return create_error_response(ERROR_MSG_MAX_RETRIES)


# ============================================================================
# 버스 위치 조회 API (버스 추적용)
# ============================================================================

def get_bus_positions(route_id: str) -> Dict[str, any]:
    """
    노선의 실시간 버스 위치 정보를 조회합니다.

    Args:
        route_id: 노선 ID (예: "100100124")

    Returns:
        Dict: API 응답
            - success (bool): 성공 여부
            - data (List[Dict]): 버스 위치 정보 리스트
                - vehicle_no: 차량 번호
                - station_seq: 정류장 순서
                - station_name: 정류장명
                - lat: 위도
                - lon: 경도
                - congestion: 혼잡도
                - bus_type: 버스 타입 (0:일반, 1:저상)
                - low_floor: 저상버스 여부 (Y/N)
            - error_message (str): 에러 메시지 (실패 시)
    """
    # API 키 확인
    if not API_KEY:
        return {
            "success": False,
            "data": [],
            "error_message": ERROR_MSG_NO_API_KEY
        }

    try:
        # API 요청 파라미터
        params = {
            'serviceKey': API_KEY,
            'busRouteId': route_id
        }

        response = requests.get(
            BUS_POSITION_API_URL,
            params=params,
            timeout=API_TIMEOUT_SECONDS
        )

        # HTTP 상태 코드 체크
        if response.status_code == HTTP_UNAUTHORIZED:
            return {
                "success": False,
                "data": [],
                "error_message": ERROR_MSG_AUTH_FAILED
            }
        elif response.status_code == HTTP_FORBIDDEN:
            return {
                "success": False,
                "data": [],
                "error_message": ERROR_MSG_ACCESS_DENIED
            }
        elif response.status_code == HTTP_NOT_FOUND:
            return {
                "success": False,
                "data": [],
                "error_message": ERROR_MSG_NOT_FOUND
            }
        elif response.status_code != HTTP_OK:
            return {
                "success": False,
                "data": [],
                "error_message": f"❌ HTTP {response.status_code} 오류"
            }

        # XML 파싱
        return _parse_bus_position_data(response.text)

    except requests.Timeout:
        return {
            "success": False,
            "data": [],
            "error_message": ERROR_MSG_TIMEOUT
        }
    except requests.ConnectionError:
        return {
            "success": False,
            "data": [],
            "error_message": ERROR_MSG_CONNECTION
        }
    except Exception as e:
        return {
            "success": False,
            "data": [],
            "error_message": f"❌ 예상치 못한 오류: {str(e)}"
        }


def _parse_bus_position_data(xml_text: str) -> Dict[str, any]:
    """
    버스 위치 API의 XML 응답을 파싱합니다.

    XML 구조:
    <ServiceResult>
        <msgHeader>
            <resultCode>0</resultCode>
        </msgHeader>
        <msgBody>
            <itemList>
                <vehId>차량번호</vehId>
                <stOrd>정류장순서</stOrd>
                <stNm>정류장명</stNm>
                <gpsX>경도</gpsX>
                <gpsY>위도</gpsY>
                <congetion>혼잡도</congetion>
                <busType>버스타입</busType>
                <isFullFlag>저상버스여부</isFullFlag>
            </itemList>
        </msgBody>
    </ServiceResult>

    Args:
        xml_text: XML 응답 텍스트

    Returns:
        Dict: 파싱된 응답
    """
    try:
        root = ET.fromstring(xml_text)

        # 결과 코드 확인 (headerCd 사용)
        header_cd = root.find('.//headerCd')

        if header_cd is None or header_cd.text != API_SUCCESS_CODE:
            error_msg = root.find('.//headerMsg')
            return {
                "success": False,
                "data": [],
                "error_message": f"❌ API 오류: {error_msg.text if error_msg is not None else '알 수 없음'}"
            }

        # 버스 위치 데이터 추출
        buses = []
        for item in root.findall('.//itemList'):
            # 혼잡도 변환 (0=여유, 1=보통, 2=혼잡, 3=매우혼잡)
            congetion_code = _get_xml_text(item, 'congetion', '0')
            congetion_map = {'0': '여유', '1': '보통', '2': '혼잡', '3': '매우혼잡'}
            congetion_text = congetion_map.get(congetion_code, '정보없음')

            bus_data = {
                "vehicle_no": _get_xml_text(item, 'plainNo', 'N/A'),
                "station_seq": int(_get_xml_text(item, 'sectOrd', '0')),
                "station_name": f"{int(_get_xml_text(item, 'sectOrd', '0'))}번째 정류장",
                "lon": float(_get_xml_text(item, 'gpsX', '0')),
                "lat": float(_get_xml_text(item, 'gpsY', '0')),
                "congestion": congetion_text,
                "bus_type": _get_xml_text(item, 'busType', '0'),
                "low_floor": _get_xml_text(item, 'isFullFlag', '0')
            }
            buses.append(bus_data)

        return {
            "success": True,
            "data": buses,
            "error_message": ""
        }

    except ET.ParseError:
        return {
            "success": False,
            "data": [],
            "error_message": ERROR_MSG_PARSE_FAILED
        }
    except Exception as e:
        return {
            "success": False,
            "data": [],
            "error_message": f"❌ 파싱 오류: {str(e)}"
        }


def _get_xml_text(element: ET.Element, tag: str, default: str) -> str:
    """
    XML 요소에서 안전하게 텍스트를 추출합니다.

    Args:
        element: XML 요소
        tag: 태그 이름
        default: 기본값

    Returns:
        str: 추출된 텍스트 또는 기본값
    """
    child = element.find(tag)
    return child.text if child is not None and child.text else default
