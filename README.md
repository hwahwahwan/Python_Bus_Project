# 🚌 버스 정류소 위치 조회 및 실시간 버스 위치 프로젝트

서울시 버스 정류소 위치 정보와 실시간 버스 위치를 조회하는 Python 프로젝트입니다.

---

## 📁 프로젝트 구조

```
project/
├── README.md                      # 프로젝트 메인 문서
├── ARCHITECTURE.md                # 아키텍처 및 설계 문서
├── app.py                         # ✅ 메인 Streamlit 애플리케이션
├── .env                          # 환경변수 (API 키 등)
├── .env.example                  # 환경변수 예시 파일
├── .gitignore                    # Git 제외 파일 목록
├── requirements.txt              # Python 패키지 의존성
│
├── src/                          # 🎯 소스 코드 루트
│   ├── utils/                    # 공통 유틸리티
│   │   ├── constants.py          # 전역 상수 정의
│   │   └── validators.py         # 데이터 검증 함수
│   │
│   ├── core/                     # 핵심 비즈니스 로직
│   │   ├── data_loader.py        # CSV 데이터 로드 및 필터링
│   │   └── session_manager.py    # 세션 상태 관리
│   │
│   ├── api/                      # 외부 API 연동
│   │   ├── api_config.py         # API 설정
│   │   └── bus_api.py            # ✅ 서울시 버스 API 호출
│   │
│   └── ui/                       # UI 컴포넌트
│       ├── sidebar.py            # ✅ 왼쪽 사이드바 (검색)
│       ├── bus_cards.py          # ✅ 버스 도착 정보 카드
│       └── map_view.py           # ✅ 지도 뷰 (PyDeck)
│
├── data/                         # 📊 데이터 폴더
│   ├── stops.csv                 # 원본: 서울시 버스 정류소 위치 정보
│   ├── routes.csv                # 원본: 버스 노선 정보
│   ├── route_stations.csv        # 원본: 노선별 정류소 정보
│   └── stops_processed.csv       # ✅ 전처리 완료: 정류소 데이터 (12,859개)
│
├── preprocessing/                # 🛠️ 데이터 전처리 모듈
│   ├── README.md                 # 전처리 프로세스 가이드
│   ├── utils.py                  # 공통 유틸리티 함수
│   ├── kakao_api.py              # 카카오 로컬 API 모듈
│   └── preprocess_stops.py       # 메인 전처리 스크립트
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
- 버스 정류소 데이터 정제 및 변환
- ARS_ID 5자리 제로패딩
- 카카오 로컬 API를 통한 지역 정보 추출 (API에서도 찾을 수 없는 21개 행 삭제)
- 정류소명 + ARS_ID 병합 (중복 방지)

### 2. 실시간 버스 대시보드 ✅
- **3단계 필터링**: 지역(구) 선택 → 정류장명 검색 → 정류장 선택
- **실시간 버스 도착 정보**: 서울시 공공데이터 API 연동
- **버스 카드 그리드**: 최대 4대까지 도착 정보 표시
  - 버스 번호, 방면, 도착 시간
  - 저상버스 구분 (초록색 배지)
  - 막차 여부 표시
  - 첫 번째 버스는 파란색으로 강조
- **지도 시각화**: PyDeck을 사용한 정류장 위치 표시
  - 확대/축소에 관계없이 일정한 크기의 마커
  - Mapbox 기반 도로 지도
- **자동 새로고침**: 정류장 선택 시 자동으로 버스 정보 조회
- **반응형 UI**: 프로토타입 디자인 기반의 깔끔한 카드 레이아웃

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

**API 엔드포인트**: `http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid`

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

