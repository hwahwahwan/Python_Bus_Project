# 🚌 서울시 실시간 버스 대시보드

서울시 버스 정류소 위치 정보와 실시간 버스 위치 추적을 제공하는 Streamlit 기반 대시보드입니다.

---

## 📁 프로젝트 구조

> 📖 상세한 구조는 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)를 참고하세요.

```
project/
├── README.md                      # 프로젝트 메인 문서
├── CHANGELOG.md                   # ✅ 변경 이력
├── PROJECT_STRUCTURE.md           # ✅ 프로젝트 구조 상세 가이드
├── test_bus_tracker.py            # ✅ 버스 추적 기능 테스트
├── test_results_summary.md        # ✅ 테스트 결과 요약
├── app.py                         # ✅ 메인 Streamlit 애플리케이션
├── .env                          # 환경변수 (API 키 등)
├── .env.example                  # 환경변수 예시 파일
├── .gitignore                    # Git 제외 파일 목록
├── requirements.txt              # Python 패키지 의존성
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
│       ├── bus_cards.py          # ✅ 버스 도착 정보 카드
│       ├── map_view.py           # ✅ 지도 뷰 (PyDeck)
│       └── bus_tracker.py        # ✅ 실시간 버스 위치 추적
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
├── venv/                         # 🐍 Python 가상환경
│
└── 작업계획/                      # 📝 프로젝트 계획 및 문서
    ├── 1127.txt                  # 작업 계획
    └── 발표자료 정리/
        └── 데이터 전처리 알고리즘.txt
```

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
- **지도 시각화**: PyDeck을 사용한 정류장 위치 표시
- **자동 새로고침**: 정류장 선택 시 자동으로 버스 정보 조회

### 3. 실시간 버스 위치 추적 ✅ NEW!
- **노선별 버스 추적**: 선택한 노선의 모든 운행 버스 실시간 위치 표시
- **지도 시각화**:
  - 노선 경로 표시 (초록색 PathLayer)
  - 버스 위치 마커 (빨간색 ScatterplotLayer)
  - 정류장 위치 마커 (파란색)
- **실시간 정보 테이블**:
  - 차량번호, 버스 유형 (일반/저상)
  - 현재 위치 (정류장 순서)
  - 혼잡도 정보 (여유/보통/혼잡/매우혼잡)
  - GPS 좌표 (위도/경도)
- **자동 새로고침 기능**:
  - 60초마다 자동 API 호출
  - 5초마다 화면 갱신으로 부드러운 업데이트
  - 수동 새로고침 버튼 제공
- **스마트 노선 필터링**:
  - 정류장 선택 시 해당 정류장을 경유하는 노선만 표시
  - 전체 노선 목록 조회 가능

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

### 버스 위치 추적 기능 개선

#### 1. HTML 테이블 렌더링 수정 ✅
- **문제**: 차량 운행 정보가 HTML 태그로 표시됨
- **해결**: 자동 새로고침 로직 최적화로 정상 렌더링

#### 2. API 호출 최적화 ✅
- 호출 간격: 30초 → **60초**로 변경
- 서버 부하 감소 및 API 사용량 최적화

#### 3. 자동 새로고침 로직 개선 ✅
- API는 60초마다 호출
- 화면은 5초마다 갱신하여 부드러운 업데이트 제공
- 불필요한 rerun 제거로 성능 향상

#### 4. 지도 깜빡임 해결 ✅
- 1초마다 rerun → 5초 간격으로 변경
- 흰색 깜빡임 현상 대폭 감소
- 사용자 경험 개선

#### 5. PyDeck Deprecated 경고 해결 ✅
- `get_color` → `get_fill_color`로 변경
- 최신 PyDeck API 스펙 적용

### 테스트
전체 기능 테스트를 위한 스크립트 제공:
```bash
source venv/bin/activate
python test_bus_tracker.py
```

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

