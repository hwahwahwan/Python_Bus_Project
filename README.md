# 🚌 서울시 실시간 버스 대시보드

> 서울시 버스 정류소 위치 정보와 실시간 버스 위치 추적을 제공하는 Streamlit 기반 대시보드

<br>

## 🖥️ 미리보기

<img width="798" height="501" alt="Image" src="https://github.com/user-attachments/assets/5682b55d-7ce6-4647-9115-79e507bbd4cf" />

<img width="797" height="497" alt="Image" src="https://github.com/user-attachments/assets/be0038fc-8d63-4ead-bf94-993d3ce17eb6" />

<img width="798" height="496" alt="Image" src="https://github.com/user-attachments/assets/69568261-6aa6-48e7-838a-6558b9c9be91" />

<img width="800" height="500" alt="Image" src="https://github.com/user-attachments/assets/39a88a56-1dab-4a5f-a442-e115cfb87d48" />

<br>

## 👥 팀원

| 이름 | 역할 | GitHub |
|------|------|--------|
| 정용환 | 풀스택 개발 | [@hwahwahwan](https://github.com/hwahwahwan) |

<br>

## 🛠️ 개발환경

| 항목 | 버전 |
|------|------|
| Python | 3.x |
| OS | macOS |
| IDE | VS Code |

<br>

## 💡 채택기술

**Frontend / Visualization**

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![PyDeck](https://img.shields.io/badge/PyDeck-3A76F0?style=for-the-badge&logo=mapbox&logoColor=white)

**Backend / Data**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

**API**

![Kakao](https://img.shields.io/badge/Kakao_Local_API-FFCD00?style=for-the-badge&logo=kakao&logoColor=black)
![Seoul](https://img.shields.io/badge/서울_열린데이터광장_API-0068B7?style=for-the-badge)

- **Streamlit** — 빠른 데이터 앱 UI 구성
- **PyDeck** — 지도 위 버스 위치·경로 시각화
- **Pandas** — CSV 데이터 전처리 및 필터링
- **Kakao Local API** — 정류소 지역 정보(구) 추출
- **서울 열린데이터광장 API** — 실시간 버스 도착·위치 정보

<br>

## 📁 프로젝트 구조

```
project/
├── app.py                          # 메인 Streamlit 앱
├── requirements.txt                # 패키지 의존성
├── .env.example                    # 환경변수 예시
│
├── src/
│   ├── utils/
│   │   ├── constants.py            # 전역 상수
│   │   └── validators.py           # 데이터 검증
│   ├── core/
│   │   ├── data_loader.py          # CSV 로드 및 필터링
│   │   └── session_manager.py      # 세션 상태 관리
│   ├── api/
│   │   ├── api_config.py           # API 설정
│   │   └── bus_api.py              # 서울시 버스 API 호출
│   └── ui/
│       ├── sidebar.py              # 사이드바 (정류장 검색)
│       ├── bus_cards.py            # 버스 도착 정보 카드
│       ├── map_view.py             # 지도 뷰
│       └── bus_tracker.py          # 실시간 버스 위치 추적
│
├── data/
│   ├── stops_processed.csv         # 전처리 완료 정류소 데이터 (12,859개)
│   └── route_stations_processed.csv # 노선-정류소 매핑 데이터
│
├── preprocessing/
│   ├── preprocess_stops.py         # 정류장 데이터 전처리
│   └── preprocess_routes.py        # 노선 데이터 전처리
│
└── docs/                           # 프로젝트 문서
```

<br>

## 🧩 역할분담

| 이름 | 담당 영역 |
|------|-----------|
| 정용환 | 데이터 전처리 / API 연동 / UI 개발 / 지도 시각화 / 실시간 버스 추적 |

<br>

## 📅 개발기간

| 항목 | 기간 |
|------|------|
| 전체 개발 | 2025.11.15 ~ 2025.11.28 |
| 데이터 전처리 | 2025.11.15 ~ 2025.11.17 |
| 정류장 조회 기능 | 2025.11.18 ~ 2025.11.22 |
| 실시간 버스 추적 기능 | 2025.11.23 ~ 2025.11.28 |

<br>

## 🎯 주요기능

### 1. 정류장 조회 및 버스 도착 정보
- **3단계 필터링**: 지역(구) 선택 → 정류장명 검색 → 정류장 선택
- 실시간 버스 도착 정보 카드 (최대 4대)
  - 버스 번호, 방면, 도착 시간 표시
  - 저상버스 구분 (초록색 배지), 막차 여부 표시
  - 첫 번째 버스 파란색 강조
- PyDeck 기반 정류장 위치 지도 표시
- **🔍 추적 버튼**: 카드에서 바로 해당 버스 실시간 추적 연동

### 2. 실시간 버스 위치 추적
- 선택 노선의 모든 운행 버스 실시간 위치 표시
- 지도 시각화
  - 노선 경로 (초록색 PathLayer)
  - 버스 위치 마커 (빨간색 ScatterplotLayer)
  - 정류장 위치 마커 (파란색)
- **부드러운 마커 애니메이션**: 0.5초마다 선형 보간으로 자연스러운 이동 표현
- 실시간 정보 테이블 (차량번호, 버스 유형, 현재 위치, 혼잡도, GPS 좌표)
- 자동 새로고침: 60초마다 API 호출 / 0.5초마다 화면 갱신

### 3. 데이터 전처리
- ARS_ID 5자리 제로패딩
- 카카오 로컬 API로 지역 정보(구) 추출
- 정류소명 + ARS_ID 병합 (중복 방지)
- 총 12,859개 정류소 데이터 구축

<br>

## 🚀 시작하기

### 1. 패키지 설치

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일에 아래 키를 입력합니다:

```
KAKAO_API_KEY=카카오_REST_API_키
DATA_PORTAL_KEY=서울_열린데이터광장_인증키
```

> **API 키 발급**
> - 카카오: [kakao developers](https://developers.kakao.com/) → 앱 설정 → REST API 키
> - 서울 열린데이터광장: [data.seoul.go.kr](https://data.seoul.go.kr/) → "버스도착정보조회 서비스" 검색 후 인증키 신청

### 3. 앱 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

<br>

---

📝 이 프로젝트는 교육 목적으로 제작되었습니다.
