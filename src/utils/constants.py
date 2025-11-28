"""
전역 상수 정의

이 모듈은 프로젝트 전반에서 사용되는 상수들을 중앙 집중식으로 관리합니다.
매직 넘버를 제거하고 유지보수성을 향상시키기 위한 목적입니다.
"""

# ============================================================================
# 데이터 관련 상수
# ============================================================================
DATA_PATH = "data/stops_processed.csv"
STATION_ID_DTYPE = "str"
ARS_ID_DTYPE = "str"

# ============================================================================
# API 관련 상수
# ============================================================================
BUS_API_URL = "http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid"
API_TIMEOUT_SECONDS = 10
API_MAX_RETRIES = 3
API_RETRY_DELAY_SECONDS = 1

# HTTP 상태 코드
HTTP_OK = 200
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404

# API 응답 코드
API_SUCCESS_CODE = "0"

# ============================================================================
# UI 관련 상수
# ============================================================================
# 페이지 설정
PAGE_TITLE = "서울시 실시간 버스 대시보드"
PAGE_ICON = "🚌"
LAYOUT_MODE = "wide"

# 버스 카드 표시
MAX_DISPLAY_BUSES = 4

# 지도 설정
DEFAULT_ZOOM_LEVEL = 15
MAP_POINT_COLOR = [0, 100, 255, 200]  # 파란색 RGBA
MAP_POINT_RADIUS = 15
MAP_STYLE = "light"  # PyDeck 내장 스타일 (Mapbox 토큰 불필요)

# ============================================================================
# 버스 타입 상수
# ============================================================================
BUS_TYPE_NORMAL = "0"
BUS_TYPE_LOW_FLOOR = "1"
BUS_TYPE_ARTICULATED = "2"

# 버스 타입 아이콘
BUS_TYPE_ICONS = {
    BUS_TYPE_NORMAL: "🔵 일반",
    BUS_TYPE_LOW_FLOOR: "🟢 저상",
    BUS_TYPE_ARTICULATED: "🟡 굴절"
}

# 막차 표시
LAST_BUS_FLAG_YES = "Y"
LAST_BUS_FLAG_NO = "N"
LAST_BUS_ICON = "🚨 막차"

# ============================================================================
# 메시지 상수
# ============================================================================
# 에러 메시지
ERROR_MSG_NO_API_KEY = "❌ API 키가 설정되지 않았습니다. .env 파일을 확인하세요."
ERROR_MSG_AUTH_FAILED = "❌ API 인증 실패 (401): API 키를 확인하세요."
ERROR_MSG_ACCESS_DENIED = "❌ API 접근 거부 (403): 권한을 확인하세요."
ERROR_MSG_NOT_FOUND = "❌ 정류소를 찾을 수 없습니다 (404)."
ERROR_MSG_TIMEOUT = "❌ API 요청 시간 초과: 네트워크를 확인하세요."
ERROR_MSG_CONNECTION = "❌ 네트워크 연결 오류: 인터넷 연결을 확인하세요."
ERROR_MSG_MAX_RETRIES = "❌ API 호출 실패: 최대 재시도 횟수 초과"
ERROR_MSG_PARSE_FAILED = "❌ API 응답 파싱 실패: XML 형식이 올바르지 않습니다."

# 경고 메시지
WARNING_MSG_NO_BUS = "⚠️ 현재 도착 예정 버스가 없습니다."
WARNING_MSG_NO_SEARCH_RESULT = "⚠️ 검색 결과가 없습니다. 다른 키워드를 입력해보세요."

# 안내 메시지
INFO_MSG_SELECT_STOP = "👈 왼쪽 사이드바에서 지역과 정류장을 선택해주세요."
INFO_MSG_REFRESH_TO_VIEW = "🔄 새로고침 버튼을 눌러 버스 정보를 조회하세요."

# 성공 메시지 템플릿
SUCCESS_MSG_TEMPLATE = "✅ {station_name}({ars_id}) 선택됨"

# ============================================================================
# 세션 상태 키
# ============================================================================
SESSION_KEY_TARGET_STOP = "target_stop"
SESSION_KEY_LAST_UPDATE = "last_update"
SESSION_KEY_PREV_REGION = "prev_region"
SESSION_KEY_BUS_DATA = "bus_data"

# ============================================================================
# 데이터 필드명
# ============================================================================
FIELD_STATION_ID = "station_id"
FIELD_ARS_ID = "ars_id"
FIELD_STATION_NAME = "station_name"
FIELD_LAT = "lat"
FIELD_LON = "lon"
FIELD_REGION_NAME = "region_name"
FIELD_DISPLAY_NAME = "display_name"

# ============================================================================
# 버스 추적 관련 상수
# ============================================================================
# API
BUS_POSITION_API_URL = "http://ws.bus.go.kr/api/rest/buspos/getBusPosByRtid"
AUTO_REFRESH_INTERVAL_SECONDS = 60
ANIMATION_INTERVAL_SECONDS = 0.5  # 마커 보간 새로고침 주기 (0.5초)

# 노선 데이터
ROUTE_STATIONS_DATA_PATH = "data/route_stations_processed.csv"

# 노선 경로 (PathLayer)
ROUTE_PATH_COLOR = [34, 139, 34]  # 초록색
ROUTE_PATH_WIDTH = 5
ROUTE_PATH_MIN_WIDTH = 2
ROUTE_PATH_MAX_WIDTH = 10

# 버스 마커 (ScatterplotLayer)
BUS_MARKER_COLOR = [255, 0, 0, 200]  # 빨간색
BUS_MARKER_RADIUS = 20

# 정류장 마커 (현재 정류장 - 파란색)
CURRENT_STOP_RADIUS = 25

# 세션 키 (버스 추적용)
SESSION_KEY_SELECTED_ROUTE = "selected_route"
SESSION_KEY_BUS_POSITIONS = "bus_positions"
SESSION_KEY_AUTO_REFRESH_ENABLED = "auto_refresh_enabled"
SESSION_KEY_LAST_API_CALL = "last_api_call"
SESSION_KEY_ROUTE_DATA = "route_data"

# ============================================================================
# 기타 상수
# ============================================================================
DEFAULT_VALUE_NO_INFO = "정보없음"
DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
