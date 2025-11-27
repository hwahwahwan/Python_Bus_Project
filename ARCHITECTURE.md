# 프로젝트 아키텍처 및 설계 문서

## 📐 설계 원칙

이 프로젝트는 다음의 클린 코드 원칙을 준수하여 개발되었습니다:

### 1. 단일 책임 원칙 (Single Responsibility Principle)
각 모듈과 함수는 하나의 명확한 책임만을 가집니다.
- `data_loader.py`: 데이터 로드 및 필터링만 담당
- `bus_api.py`: API 호출 및 응답 파싱만 담당
- `session_manager.py`: 세션 상태 관리만 담당

### 2. DRY (Don't Repeat Yourself)
중복 코드를 제거하고 재사용 가능한 함수로 모듈화했습니다.
- 공통 상수는 `constants.py`에 중앙 집중화
- 공통 유틸리티는 `validators.py`에 분리
- UI 컴포넌트는 독립적인 모듈로 분리

### 3. 명확한 네이밍
- **함수명**: 동사로 시작 (`get_`, `load_`, `parse_`, `render_`)
- **변수명**: 의미 있는 영문 이름 사용
- **상수**: 대문자 + 언더스코어 (`API_URL`, `MAX_RETRIES`)

### 4. 매직 넘버 제거
하드코딩된 숫자를 모두 상수로 정의했습니다.
```python
# Bad
if zoom_level == 15:

# Good
if zoom_level == DEFAULT_ZOOM_LEVEL:
```

### 5. 타입 힌팅 및 Docstring
모든 함수에 타입 힌팅과 Google Style Docstring을 추가했습니다.
```python
def filter_by_region(df: pd.DataFrame, region_name: str) -> pd.DataFrame:
    """
    지역(구)으로 데이터를 필터링합니다.

    Args:
        df: 전체 정류소 데이터
        region_name: 구 이름 (예: "강남구")

    Returns:
        pd.DataFrame: 필터링된 데이터
    """
```

### 6. 에러 처리
예외 상황을 명확하게 처리하고 사용자에게 친절한 메시지를 제공합니다.

---

## 📂 폴더 구조 및 역할

```
project/
├── app.py                          # 메인 애플리케이션 엔트리 포인트
├── .env                            # 환경변수 (gitignore에 포함)
├── .env.example                    # 환경변수 예시
├── requirements.txt                # Python 패키지 의존성
├── ARCHITECTURE.md                 # 이 파일
│
├── src/                            # 소스 코드 루트
│   ├── __init__.py
│   │
│   ├── utils/                      # 🔧 공통 유틸리티
│   │   ├── __init__.py
│   │   ├── constants.py            # 전역 상수 정의
│   │   └── validators.py           # 데이터 검증 함수
│   │
│   ├── core/                       # 💼 핵심 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── data_loader.py          # CSV 데이터 로드 및 필터링
│   │   └── session_manager.py      # Streamlit 세션 상태 관리
│   │
│   ├── api/                        # 🌐 외부 API 연동
│   │   ├── __init__.py
│   │   ├── api_config.py           # API 설정 및 환경변수
│   │   └── bus_api.py              # 서울시 버스 API 호출
│   │
│   └── ui/                         # 🎨 UI 컴포넌트
│       ├── __init__.py
│       ├── sidebar.py              # 왼쪽 사이드바 (검색)
│       ├── bus_cards.py            # 버스 도착 정보 카드
│       └── map_view.py             # 지도 뷰
│
├── data/                           # 📊 데이터
│   └── stops_processed.csv         # 전처리된 정류소 데이터
│
└── preprocessing/                  # 🛠️ 데이터 전처리 모듈 (기존)
    ├── preprocess_stops.py
    ├── kakao_api.py
    └── utils.py
```

---

## 📦 모듈 상세 설명

### src/utils/ - 공통 유틸리티

#### constants.py
**목적**: 전역 상수를 중앙 집중식으로 관리
**주요 내용**:
- API 관련 상수 (URL, 타임아웃, 재시도 횟수)
- UI 관련 상수 (페이지 제목, 아이콘, 레이아웃)
- 메시지 상수 (에러, 경고, 안내 메시지)
- 세션 키 상수
- 데이터 필드명 상수

**사용 예시**:
```python
from src.utils.constants import MAX_DISPLAY_BUSES, ERROR_MSG_NO_API_KEY
```

#### validators.py
**목적**: 데이터 유효성 검사 함수 제공
**주요 함수**:
- `is_valid_dataframe()`: DataFrame 유효성 확인
- `is_valid_ars_id()`: ARS ID 형식 검증
- `is_valid_coordinates()`: 좌표 유효성 확인
- `has_required_columns()`: 필수 컬럼 존재 여부 확인

---

### src/core/ - 핵심 비즈니스 로직

#### data_loader.py
**목적**: CSV 데이터 로드 및 필터링
**주요 함수**:
- `load_stops_data()`: 정류소 데이터 로드 (캐싱)
- `get_region_list()`: 구 목록 추출
- `filter_by_region()`: 지역별 필터링
- `filter_by_search()`: 검색어 필터링
- `get_stop_by_display_name()`: 정류장 조회

**특징**:
- `@st.cache_data` 데코레이터로 성능 최적화
- 데이터 유효성 검증 내장

#### session_manager.py
**목적**: Streamlit 세션 상태 관리
**주요 함수**:
- `initialize_session_state()`: 세션 초기화
- `get_target_stop()`, `set_target_stop()`: 선택된 정류장 관리
- `get_last_update()`, `set_last_update()`: 업데이트 시간 관리
- `check_and_reset_on_region_change()`: 지역 변경 감지 및 초기화
- `is_stop_selected()`: 정류장 선택 여부 확인

**세션 수명 주기**:
1. 앱 시작 → `initialize_session_state()` 호출
2. 지역 변경 → 자동 초기화
3. 브라우저 새로고침 → 완전 초기화

---

### src/api/ - 외부 API 연동

#### api_config.py
**목적**: API 설정 및 환경변수 관리
**주요 함수**:
- `get_bus_api_key()`: API 키 반환
- `get_bus_api_url()`: API URL 반환

**환경변수**:
- `DATA_PORTAL_KEY`: 서울시 공공데이터포털 API 키

#### bus_api.py
**목적**: 서울시 버스 도착 정보 API 호출
**주요 함수**:
- `get_bus_arrival_info()`: 버스 도착 정보 조회
- `parse_bus_data()`: XML 응답 파싱
- `create_error_response()`: 에러 응답 생성
- `create_success_response()`: 성공 응답 생성

**에러 처리**:
- HTTP 상태 코드별 명확한 에러 메시지
- 자동 재시도 로직 (최대 3회)
- 타임아웃 처리
- XML 파싱 예외 처리

**API 엔드포인트**:
```
http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid
파라미터: serviceKey, arsId
```

---

### src/ui/ - UI 컴포넌트

#### sidebar.py
**목적**: 왼쪽 사이드바 렌더링
**주요 함수**:
- `render_sidebar()`: 전체 사이드바 렌더링

**구성**:
1. 지역(구) 선택 드롭다운
2. 정류장명 검색 입력창
3. 정류장 선택 드롭다운
4. 선택 피드백 메시지
5. 키보드 단축키 안내

#### bus_cards.py
**목적**: 버스 도착 정보 카드 렌더링
**주요 함수**:
- `render_bus_arrival_section()`: 전체 섹션 렌더링
- `render_bus_card()`: 개별 버스 카드 렌더링
- `calculate_grid_layout()`: 그리드 레이아웃 계산
- `get_bus_type_icon()`: 버스 타입 아이콘 반환

**그리드 레이아웃**:
- 1대: 1열
- 2대: 2열
- 3대: 3열
- 4대 이상: 4열 (최대 4대까지 표시)

**카드 내용**:
- 버스 번호
- 버스 타입 (일반/저상/굴절)
- 막차 여부
- 방면 정보
- 첫 번째/두 번째 버스 도착 시간

#### map_view.py
**목적**: 지도 뷰 렌더링
**주요 함수**:
- `render_map_section()`: 전체 지도 섹션 렌더링
- `create_map_deck()`: PyDeck Deck 객체 생성
- `create_view_state()`: 지도 뷰 상태 생성
- `create_map_layer()`: ScatterplotLayer 생성

**지도 설정**:
- 기본 줌 레벨: 15 (동네 수준)
- 마커 색상: 파란색 (RGB: 0, 100, 255)
- 마커 반지름: 50 (자동 스케일링)
- 스타일: Mapbox Streets

---

## 🔄 데이터 흐름

### 1. 앱 시작
```
app.py
  ├─> configure_page() (페이지 설정)
  ├─> initialize_session_state() (세션 초기화)
  └─> load_stops_data() (데이터 로드)
```

### 2. 사이드바 렌더링
```
render_sidebar()
  ├─> get_region_list() (구 목록 추출)
  ├─> filter_by_region() (지역 필터링)
  ├─> filter_by_search() (검색 필터링)
  ├─> get_stop_by_display_name() (정류장 조회)
  └─> set_target_stop() (세션에 저장)
```

### 3. 버스 정보 조회
```
render_bus_arrival_section()
  ├─> get_bus_arrival_info() (API 호출)
  │     ├─> parse_bus_data() (응답 파싱)
  │     └─> create_success_response()
  ├─> set_bus_data() (세션에 저장)
  ├─> set_last_update() (시간 기록)
  └─> render_bus_card() (카드 렌더링)
```

### 4. 지도 렌더링
```
render_map_section()
  ├─> create_map_deck()
  │     ├─> create_view_state()
  │     └─> create_map_layer()
  └─> st.pydeck_chart()
```

---

## 🎯 주요 기능 흐름도

### 정류장 선택 흐름
```
사용자 → 지역 선택
       ↓
     지역 변경 감지
       ↓
     이전 데이터 초기화
       ↓
     검색어 입력 (선택적)
       ↓
     필터링된 목록 표시
       ↓
     정류장 선택
       ↓
     세션에 저장
       ↓
     피드백 메시지 표시
```

### API 호출 흐름
```
새로고침 버튼 클릭
       ↓
     API 키 확인
       ↓
     HTTP 요청 (최대 3회 재시도)
       ↓
     응답 코드 확인
       ↓
     XML 파싱
       ↓
     버스 데이터 추출
       ↓
     세션에 저장
       ↓
     UI 업데이트
```

---

## 🧪 에러 처리 전략

### 1. 데이터 로드 에러
- 파일 없음 → 명확한 경로 표시
- 빈 데이터 → 유효성 검증 에러
- 필수 컬럼 누락 → 누락된 컬럼 목록 표시

### 2. API 호출 에러
- 401/403 → API 키 확인 안내
- 404 → 정류소 정보 확인 안내
- 타임아웃 → 네트워크 확인 안내
- 연결 오류 → 인터넷 연결 확인 안내

### 3. UI 렌더링 에러
- 지도 로드 실패 → 에러 메시지 표시
- 검색 결과 없음 → 경고 메시지 표시
- 버스 없음 → 정보 메시지 표시

---

## 🚀 실행 방법

### 1. 환경 설정
```bash
# 패키지 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일에 API 키 입력
```

### 2. 앱 실행
```bash
streamlit run app.py
```

### 3. 브라우저 접속
```
http://localhost:8501
```

---

## 📊 성능 최적화

### 1. 데이터 캐싱
`@st.cache_data` 데코레이터를 사용하여 CSV 재로드 방지

### 2. 세션 상태 활용
사용자 선택 및 API 응답을 세션에 저장하여 불필요한 재호출 방지

### 3. 모듈 분리
독립적인 모듈로 분리하여 로딩 시간 최소화

---

## 🔐 보안 고려사항

### 1. API 키 관리
- `.env` 파일을 `.gitignore`에 추가
- `.env.example`로 예시만 제공
- 환경변수로 주입하여 코드에 하드코딩 방지

### 2. 입력 검증
- ARS ID 형식 검증
- 좌표 유효성 확인
- SQL 인젝션 방지 (API 사용으로 해당 없음)

---

## 📈 향후 개선 방향

### 1. 기능 추가
- 즐겨찾기 기능
- 버스 노선 조회
- 알림 기능 (도착 X분 전 알림)

### 2. 성능 개선
- API 응답 캐싱
- 백그라운드 자동 갱신

### 3. UX 개선
- 로딩 스피너 개선
- 애니메이션 추가
- 다크 모드 지원

---

## 👥 기여자

- 개발자: 소프트웨어학과 정용환
- 프로젝트 기간: 2025.11

---

## 📝 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.
