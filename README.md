# 🚌 서울시 실시간 버스 대시보드

서울시 버스 정류소 위치 정보와 실시간 버스 위치 추적을 제공하는 Streamlit 기반 대시보드입니다.

---

## 📁 프로젝트 구조

```
project/
├── README.md                      # 프로젝트 메인 문서 (시작 가이드)
├── app.py                         # ✅ 메인 Streamlit 애플리케이션
├── test_bus_tracker.py            # ✅ 버스 추적 기능 테스트 스크립트
├── .env                          # 환경변수 (API 키 등)
├── .env.example                  # 환경변수 예시 파일
├── .gitignore                    # Git 제외 파일 목록
├── requirements.txt              # Python 패키지 의존성
│
├── docs/                         # 📚 프로젝트 문서
│   ├── CHANGELOG.md              # 변경 이력 (버전별 업데이트 내용)
│   ├── PROJECT_STRUCTURE.md      # 프로젝트 구조 상세 가이드
│   ├── ARCHITECTURE.md           # 아키텍처 설계 문서
│   ├── PROJECT_SUMMARY.md        # 프로젝트 요약 문서
│   └── test_results_summary.md   # 테스트 결과 요약
│
├── src/                          # 🎯 소스 코드 루트
│   ├── utils/                    # 공통 유틸리티
│   │   ├── constants.py          # ✅ 전역 상수 정의
│   │   └── validators.py         # 데이터 검증 함수
│   │
│   ├── core/                     # 핵심 비즈니스 로직
│   │   ├── data_loader.py        # ✅ CSV 데이터 로드 및 필터링
│   │   └── session_manager.py    # ✅ 세션 상태 관리
│   │
│   ├── api/                      # 외부 API 연동
│   │   ├── api_config.py         # API 설정
│   │   └── bus_api.py            # ✅ 서울시 버스 API 호출 (도착 정보 + 위치 정보)
│   │
│   └── ui/                       # UI 컴포넌트
│       ├── sidebar.py            # ✅ 왼쪽 사이드바 (검색)
│       ├── bus_cards.py          # ✅ 버스 도착 정보 카드 (추적 버튼 포함)
│       ├── map_view.py           # ✅ 지도 뷰 (PyDeck)
│       └── bus_tracker.py        # ✅ 실시간 버스 위치 추적 (애니메이션)
│
├── data/                         # 📊 데이터 폴더
│   ├── stops.csv                 # 원본: 서울시 버스 정류소 위치 정보
│   ├── routes.csv                # 원본: 버스 노선 정보
│   ├── route_stations.csv        # 원본: 노선별 정류소 정보
│   ├── stops_processed.csv       # ✅ 전처리 완료: 정류소 데이터 (12,859개)
│   └── route_stations_processed.csv  # ✅ 전처리 완료: 노선-정류소 매핑 데이터
│
├── preprocessing/                # 🛠️ 데이터 전처리 모듈
│   ├── README.md                 # 전처리 프로세스 가이드
│   ├── utils.py                  # 공통 유틸리티 함수
│   ├── kakao_api.py              # 카카오 로컬 API 모듈
│   ├── preprocess_stops.py       # 정류장 데이터 전처리 스크립트
│   └── preprocess_routes.py      # ✅ 노선 데이터 전처리 스크립트
│
├── legacy/                       # 🗄️ 레거시 코드 (참고용)
│
├── venv/                         # 🐍 Python 가상환경
│
└── 작업계획/                      # 📝 프로젝트 계획 및 문서
    ├── 1127.txt                  # 작업 계획
    └── 발표자료 정리/
        └── 데이터 전처리 알고리즘.txt
```

---

## 📚 문서 가이드

프로젝트 관련 문서는 `docs/` 폴더에 정리되어 있습니다:

| 문서 | 역할 | 언제 보면 좋을까? |
|------|------|------------------|
| **[CHANGELOG.md](docs/CHANGELOG.md)** | 버전별 변경 이력 추적 | 프로젝트 업데이트 내용을 확인할 때 |
| **[PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)** | 프로젝트 구조 상세 가이드 | 코드베이스 구조를 이해하고 싶을 때 |
| **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** | 시스템 아키텍처 설계 문서 | 전체 시스템 설계와 모듈 구조를 파악할 때 |
| **[PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)** | 프로젝트 개요 및 요약 | 프로젝트 전체 개요를 빠르게 파악할 때 |
| **[test_results_summary.md](docs/test_results_summary.md)** | 테스트 결과 요약 | 기능 테스트 결과를 확인할 때 |

---

## 🎯 주요 기능

### 1. 데이터 전처리 ✅
- **정류장 데이터 정제**
  - ARS_ID 5자리 제로패딩
  - 카카오 로컬 API를 통한 지역 정보 추출
  - 정류소명 + ARS_ID 병합 (중복 방지)
  - 총 12,859개 정류소 데이터
- **노선 데이터 전처리**
  - 노선별 정류장 순서 정보 매핑
  - 위도/경도 정보 포함
  - 버스 추적 기능에 활용

### 2. 정류장 조회 및 버스 도착 정보 ✅
- **3단계 필터링**: 지역(구) 선택 → 정류장명 검색 → 정류장 선택
- **실시간 버스 도착 정보**: 서울시 공공데이터 API 연동
- **버스 카드 그리드**: 최대 4대까지 도착 정보 표시
  - 버스 번호, 방면, 도착 시간
  - 저상버스 구분 (초록색 배지)
  - 막차 여부 표시
  - 첫 번째 버스는 파란색으로 강조
  - **🔍 추적 버튼**: 각 버스 카드에서 바로 실시간 추적 가능
- **지도 시각화**: PyDeck을 사용한 정류장 위치 표시
- **자동 새로고침**: 정류장 선택 시 자동으로 버스 정보 조회

### 3. 실시간 버스 위치 추적 ✅ NEW!
- **노선별 버스 추적**: 선택한 노선의 모든 운행 버스 실시간 위치 표시
- **지도 시각화**:
  - 노선 경로 표시 (초록색 PathLayer)
  - 버스 위치 마커 (빨간색 ScatterplotLayer)
  - 정류장 위치 마커 (파란색)
- **부드러운 마커 애니메이션**:
  - 0.5초마다 선형 보간 적용
  - 버스가 자연스럽게 이동하는 효과
  - 지도 줌/위치 상태 유지
- **실시간 정보 테이블**:
  - 차량번호, 버스 유형 (일반/저상)
  - 현재 위치 (정류장 순서)
  - 혼잡도 정보 (여유/보통/혼잡/매우혼잡)
  - GPS 좌표 (위도/경도)
- **자동 새로고침 기능**:
  - 60초마다 자동 API 호출
  - 0.5초마다 화면 갱신으로 부드러운 애니메이션
  - 수동 새로고침 버튼 제공
- **간편한 노선 선택**:
  - 정류장 조회 탭에서 버스 카드의 "🔍 추적" 버튼 클릭
  - 실시간 버스 추적 탭으로 자동 연동

---

## 🚀 시작하기

### 1. 환경 설정

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 필요 패키지 설치
pip install -r requirements.txt
# 또는 수동 설치:
# pip install streamlit pandas pydeck python-dotenv requests
```

### 2. 환경변수 설정

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일에 API 키 입력
# KAKAO_API_KEY=your_kakao_rest_api_key_here
# DATA_PORTAL_KEY=your_seoul_openapi_key_here
```

### 3. 데이터 전처리 실행 (선택사항)

```bash
# 전처리 스크립트 실행
python preprocessing/preprocess_stops.py
```

**참고**: 이미 전처리된 `data/stops_processed.csv` 파일이 있으면 이 단계는 생략 가능합니다.

### 4. 대시보드 실행

```bash
# Streamlit 앱 실행
streamlit run app.py
```

브라우저에서 자동으로 `http://localhost:8501`로 접속됩니다.

---

## 📊 데이터 정보

### 전처리 완료 데이터 (`stops_processed.csv`)

| 컬럼명 | 설명 | 예시 |
|--------|------|------|
| station_id | 정류소 ID | "108900216" |
| ars_id | ARS ID (5자리) | "09500" |
| station_name | 정류소명 | "우이동" |
| lat | 위도 | 37.6634309704 |
| lon | 경도 | 127.0122904688 |
| region_name | 구 이름 | "강북구" |
| display_name | 표시명 | "우이동(09500)" |

**총 데이터**: 12,859개 정류소

---

## 🔑 API 키 발급

### 1. 카카오 로컬 API (데이터 전처리용)
1. [카카오 개발자 사이트](https://developers.kakao.com/) 접속
2. 내 애플리케이션 > 애플리케이션 추가하기
3. 앱 설정 > 앱 키 > REST API 키 복사
4. `.env` 파일에 `KAKAO_API_KEY` 추가

### 2. 서울시 공공데이터 포털 API (실시간 버스 정보용)
1. [서울 열린데이터 광장](https://data.seoul.go.kr/) 접속
2. 회원가입 및 로그인
3. "버스도착정보조회 서비스" 검색
4. 인증키 신청 (즉시 발급)
5. `.env` 파일에 `DATA_PORTAL_KEY` 추가

**사용 중인 API 엔드포인트**:
- 버스 도착 정보: `http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid`
- 버스 위치 정보: `http://ws.bus.go.kr/api/rest/buspos/getBusPosByRtid`

---

## 🔧 최근 업데이트 (2025.11.28)

### 1. 버스 카드 클릭 기능 추가 ✅
- 각 버스 카드 하단에 **"🔍 [노선번호]번 추적"** 버튼 추가
- 버튼 클릭 시 실시간 버스 추적 탭으로 자동 연동
- 사이드바 노선 선택 UI 제거로 더 간편한 사용자 경험

### 2. 버스 마커 애니메이션 구현 ✅
- **부드러운 마커 이동**: 0.5초 간격 선형 보간 적용
- **지도 상태 유지**: 줌/위치가 60초마다 초기화되지 않음
- **API 최적화**: 60초마다 API 호출, 0.5초마다 화면 갱신

### 3. API 응답 개선 ✅
- `busRouteId` 필드 추가로 정확한 노선 ID 전달
- 버스 추적 기능 안정성 향상

### 4. PyDeck Deprecated 경고 해결 ✅
- `get_color` → `get_fill_color`로 변경
- 최신 PyDeck API 스펙 적용

### 테스트
전체 기능 테스트를 위한 스크립트 제공:
```bash
source venv/bin/activate
python test_bus_tracker.py
```

자세한 변경 이력은 [CHANGELOG.md](docs/CHANGELOG.md)를 참고하세요.

---

## 📝 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.

---

## 👥 기여자

- 개발자: 소프트웨어학과 정용환
- 프로젝트 기간: 2025.11

---

## 📞 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.
