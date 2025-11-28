# 프로젝트 구조 상세 가이드

## 📂 디렉토리 구조

```
project/
├── 📄 app.py                          # Streamlit 메인 앱
├── 📄 README.md                       # 프로젝트 소개
├── 📄 CHANGELOG.md                    # 변경 이력
├── 📄 PROJECT_STRUCTURE.md            # 이 파일
├── 📄 requirements.txt                # Python 패키지 의존성
├── 📄 .env                           # 환경변수 (API 키)
├── 📄 .env.example                   # 환경변수 예시
├── 📄 .gitignore                     # Git 제외 파일
│
├── 📁 src/                           # 소스 코드 루트
│   ├── 📁 utils/                     # 공통 유틸리티
│   │   ├── constants.py              # 전역 상수 정의
│   │   └── validators.py             # 데이터 검증
│   │
│   ├── 📁 core/                      # 핵심 비즈니스 로직
│   │   ├── data_loader.py            # 데이터 로드 및 필터링
│   │   └── session_manager.py        # Streamlit 세션 상태 관리
│   │
│   ├── 📁 api/                       # 외부 API 연동
│   │   ├── api_config.py             # API 설정 및 환경변수 로드
│   │   └── bus_api.py                # 서울시 버스 API 호출
│   │
│   └── 📁 ui/                        # UI 컴포넌트
│       ├── sidebar.py                # 정류장 검색 사이드바
│       ├── bus_cards.py              # 버스 도착 정보 카드
│       ├── map_view.py               # PyDeck 지도 시각화
│       └── bus_tracker.py            # 실시간 버스 위치 추적
│
├── 📁 data/                          # 데이터 파일
│   ├── stops.csv                     # 원본: 정류소 위치 정보
│   ├── routes.csv                    # 원본: 버스 노선 정보
│   ├── route_stations.csv            # 원본: 노선-정류소 매핑
│   ├── stops_processed.csv           # 전처리 완료: 정류소 (12,859개)
│   └── route_stations_processed.csv  # 전처리 완료: 노선-정류소 매핑
│
├── 📁 preprocessing/                 # 데이터 전처리 모듈
│   ├── README.md                     # 전처리 가이드
│   ├── utils.py                      # 공통 함수
│   ├── kakao_api.py                  # 카카오 로컬 API
│   ├── preprocess_stops.py           # 정류장 데이터 전처리
│   └── preprocess_routes.py          # 노선 데이터 전처리
│
├── 📁 venv/                          # Python 가상환경
│
├── 📄 test_bus_tracker.py            # 버스 추적 기능 테스트 스크립트
└── 📄 test_results_summary.md        # 테스트 결과 요약
```

---

## 📋 파일별 상세 설명

### 메인 애플리케이션

#### `app.py`
- Streamlit 앱 진입점
- 페이지 설정 및 탭 구성
- 2개 탭 관리:
  - 🚏 정류장 조회 (버스 도착 정보)
  - 🚌 실시간 버스 추적 (버스 위치 추적)

---

### `src/utils/` - 공통 유틸리티

#### `constants.py`
전역 상수 정의:
- 데이터 경로
- API 설정 (타임아웃, 재시도, 상태 코드)
- UI 설정 (색상, 크기, 스타일)
- 버스 타입 매핑
- 에러/경고/성공 메시지 템플릿
- 세션 상태 키
- **주요 상수**:
  - `AUTO_REFRESH_INTERVAL_SECONDS = 60` (자동 새로고침 간격)
  - `BUS_POSITION_API_URL` (버스 위치 API)
  - `MAP_STYLE = "light"` (지도 스타일)

#### `validators.py`
데이터 검증 함수:
- ARS ID 형식 검증
- 좌표 유효성 검증

---

### `src/core/` - 핵심 비즈니스 로직

#### `data_loader.py`
CSV 데이터 로드 및 필터링:
- `load_data()`: 정류장 데이터 로드 (@st.cache_data)
- `get_regions()`: 지역(구) 목록 반환
- `filter_by_region()`: 지역별 정류장 필터링
- `search_stations()`: 정류장명 검색
- `get_route_list()`: 노선 목록 반환
- `get_route_data()`: 노선 경로 데이터 로드
- `get_route_id_by_number()`: 노선 번호로 ID 조회
- `get_routes_by_stop_ars_id()`: 정류장 경유 노선 조회

#### `session_manager.py`
Streamlit 세션 상태 관리:

**정류장 조회용**:
- `initialize_session_state()`: 초기 세션 상태 설정
- `get_target_stop()`: 선택된 정류장 반환
- `set_target_stop()`: 정류장 선택 저장
- `clear_target_stop()`: 정류장 선택 해제

**버스 추적용**:
- `initialize_bus_tracking_state()`: 버스 추적 세션 초기화
- `get_selected_route()`: 선택된 노선 반환
- `set_selected_route()`: 노선 선택 저장
- `get_bus_positions()`: 버스 위치 데이터 반환
- `set_bus_positions()`: 버스 위치 데이터 저장
- `is_auto_refresh_enabled()`: 자동 새로고침 상태 확인
- `toggle_auto_refresh()`: 자동 새로고침 토글
- `should_call_api()`: API 호출 시점 확인
- `update_last_api_call()`: 마지막 API 호출 시간 업데이트

---

### `src/api/` - 외부 API 연동

#### `api_config.py`
API 설정 및 환경변수 로드:
- `.env` 파일에서 API 키 로드
- `API_KEY`: 서울시 공공데이터 API 키
- `API_URL`: 버스 도착 정보 API URL

#### `bus_api.py`
서울시 버스 API 호출:

**버스 도착 정보 조회**:
- `get_bus_arrival_info(ars_id)`: 정류소 버스 도착 정보 조회
- `parse_bus_data()`: XML 응답 파싱
- `create_error_response()`: 에러 응답 생성
- `create_success_response()`: 성공 응답 생성

**버스 위치 정보 조회** (NEW):
- `get_bus_positions(route_id)`: 노선의 실시간 버스 위치 조회
- `_parse_bus_position_data()`: 버스 위치 XML 파싱
- `_get_xml_text()`: 안전한 XML 텍스트 추출

---

### `src/ui/` - UI 컴포넌트

#### `sidebar.py`
정류장 검색 사이드바:
- `render_sidebar()`: 메인 사이드바 렌더링
- 3단계 필터링:
  1. 지역(구) 선택
  2. 정류장명 검색
  3. 정류장 선택

#### `bus_cards.py`
버스 도착 정보 카드:
- `render_bus_cards()`: 버스 카드 그리드 렌더링
- 최대 4대까지 표시
- 첫 번째 버스 파란색 강조
- 저상버스 배지
- 막차 표시

#### `map_view.py`
PyDeck 지도 시각화:
- `create_map_layer()`: 정류장 마커 레이어
- `create_bus_tracking_map()`: 버스 추적 지도
- `create_route_path_layer()`: 노선 경로 레이어 (초록색)
- `create_bus_markers_layer()`: 버스 마커 레이어 (빨간색)
- `create_current_stop_layer()`: 정류장 마커 레이어 (파란색)

#### `bus_tracker.py`
실시간 버스 위치 추적:
- `render_bus_tracker()`: 메인 화면 렌더링
- `_render_route_selector()`: 노선 선택 드롭다운
- `_render_route_info_box()`: 노선 정보 박스
- `_fetch_and_update_bus_positions()`: 버스 위치 API 호출
- `_render_map_section()`: 지도 섹션
- `_render_vehicle_table()`: HTML 차량 정보 테이블

**자동 새로고침 로직**:
- 60초마다 API 호출
- 5초마다 화면 갱신
- 부드러운 업데이트 제공

---

### `data/` - 데이터 파일

#### 원본 데이터
- `stops.csv`: 서울시 버스 정류소 원본 데이터
- `routes.csv`: 버스 노선 정보
- `route_stations.csv`: 노선별 정류소 정보

#### 전처리 데이터
- `stops_processed.csv`: 정류소 데이터 (12,859개)
  - 컬럼: station_id, ars_id, station_name, lat, lon, region_name, display_name
- `route_stations_processed.csv`: 노선-정류소 매핑
  - 컬럼: route_id, route_name, station_seq, station_name, lat, lon

---

### `preprocessing/` - 데이터 전처리

#### `preprocess_stops.py`
정류장 데이터 전처리:
1. ARS ID 5자리 제로패딩
2. 카카오 로컬 API로 지역 정보 추출
3. display_name 생성 (정류소명 + ARS ID)

#### `preprocess_routes.py`
노선 데이터 전처리:
1. 노선-정류소 매핑
2. GPS 좌표 추가
3. 정류장 순서 정렬

---

## 🔄 데이터 흐름

### 정류장 조회 플로우
```
사용자 입력
  ↓
sidebar.py (지역 선택, 검색, 정류장 선택)
  ↓
session_manager.py (선택된 정류장 저장)
  ↓
bus_api.py (버스 도착 정보 API 호출)
  ↓
bus_cards.py (카드 그리드 렌더링)
  ↓
map_view.py (지도 표시)
```

### 버스 위치 추적 플로우
```
사용자 입력
  ↓
bus_tracker.py (노선 선택)
  ↓
data_loader.py (노선 데이터 로드)
  ↓
bus_api.py (버스 위치 API 호출) [60초마다]
  ↓
session_manager.py (버스 위치 저장)
  ↓
map_view.py (지도 렌더링: 노선 경로 + 버스 마커)
  ↓
bus_tracker.py (HTML 테이블 렌더링)
  ↓
자동 새로고침 (5초마다 화면 갱신)
```

---

## 🧪 테스트

### 테스트 스크립트
- `test_bus_tracker.py`: 버스 추적 기능 종합 테스트
  - API 호출 테스트
  - HTML 테이블 생성 테스트
  - 설정 검증 테스트

### 실행 방법
```bash
source venv/bin/activate
python test_bus_tracker.py
```

---

## 📦 의존성

### 주요 패키지
- `streamlit>=1.28.0`: 웹 앱 프레임워크
- `pandas>=2.0.0`: 데이터 처리
- `pydeck>=0.8.0`: 지도 시각화
- `python-dotenv>=1.0.0`: 환경변수 관리
- `requests>=2.31.0`: HTTP 요청

---

## 🔑 환경변수

### `.env` 파일
```
DATA_PORTAL_KEY=your_seoul_api_key_here
KAKAO_API_KEY=your_kakao_api_key_here
```

---

## 📊 주요 기능별 파일 매핑

### 정류장 조회
- UI: `sidebar.py`, `bus_cards.py`, `map_view.py`
- Logic: `session_manager.py`, `data_loader.py`
- API: `bus_api.py::get_bus_arrival_info()`

### 버스 위치 추적
- UI: `bus_tracker.py`, `map_view.py`
- Logic: `session_manager.py`, `data_loader.py`
- API: `bus_api.py::get_bus_positions()`

### 데이터 전처리
- Scripts: `preprocessing/preprocess_stops.py`, `preprocessing/preprocess_routes.py`
- API: `preprocessing/kakao_api.py`

---

**마지막 업데이트**: 2025.11.28
