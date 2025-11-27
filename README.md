# 🚌 버스 정류소 위치 조회 및 실시간 버스 위치 프로젝트

서울시 버스 정류소 위치 정보와 실시간 버스 위치를 조회하는 Python 프로젝트입니다.

---

## 📁 프로젝트 구조

```
project/
├── README.md                      # 프로젝트 메인 문서
├── .env                          # 환경변수 (API 키 등)
├── .env.example                  # 환경변수 예시 파일
├── .gitignore                    # Git 제외 파일 목록
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

### 1. 데이터 전처리
- 버스 정류소 데이터 정제 및 변환
- ARS_ID 5자리 제로패딩
- 카카오 로컬 API를 통한 지역 정보 추출 (API에서도 찾을 수 없는 21개 행 삭제)
- 정류소명 + ARS_ID 병합 (중복 방지)

### 2. 버스 위치 조회 (개발 예정)
- 실시간 버스 위치 조회
- 정류소별 버스 도착 정보

---

## 🚀 시작하기

### 1. 환경 설정

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 필요 패키지 설치
pip install pandas python-dotenv requests
```

### 2. 환경변수 설정

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일에 API 키 입력
# KAKAO_API_KEY=your_kakao_rest_api_key_here
```

### 3. 데이터 전처리 실행

```bash
# 전처리 스크립트 실행
python preprocessing/preprocess_stops.py
```

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

### 카카오 로컬 API
1. [카카오 개발자 사이트](https://developers.kakao.com/) 접속
2. 내 애플리케이션 > 애플리케이션 추가하기
3. 앱 설정 > 앱 키 > REST API 키 복사
4. `.env` 파일에 추가

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

