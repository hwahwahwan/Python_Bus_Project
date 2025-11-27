# 버스 정류소 데이터 전처리

이 폴더는 버스 정류소 위치 데이터를 전처리하는 스크립트들을 포함합니다.

## 📁 파일 구조

```
preprocessing/
├── README.md                 # 이 파일
├── preprocess_stops.py       # 메인 실행 파일
├── kakao_api.py             # 카카오 로컬 API 모듈
└── utils.py                 # 공통 유틸리티 함수
```

## 🎯 전처리 프로세스

### 1. **데이터 로드**
- `stops.csv` 파일을 읽어옵니다
- 모든 ID 컬럼을 문자열로 강제 변환합니다

### 2. **ARS_ID 제로패딩**
- ARS_ID를 5자리로 맞춥니다
- 예: `123` → `00123`

### 3. **결측치 및 이상치 제거**
- 좌표(`lat`, `lon`) 또는 정류소명(`station_name`)이 NULL인 행 삭제
- 좌표가 0이거나 유효하지 않은 행 삭제

### 4. **region_name 채우기**
- `region_name`이 비어있는 행에 대해 카카오 로컬 API로 주소 조회
- 주소에서 '구' 정보만 추출 (예: "서울특별시 강남구" → "강남구")

### 5. **display_name 생성**
- 정류소명과 ARS_ID를 병합한 새 컬럼 생성
- 형식: `{정류소명}({ARS_ID})`
- 예: `강남역(23111)`

### 6. **데이터 저장**
- 전처리된 데이터를 `stops_processed.csv`로 저장

## 🚀 사용법

### 1. 환경 설정

```bash
# 1. 필요한 패키지 설치
pip install pandas python-dotenv requests

# 2. 환경변수 파일 생성
cp ../.env.example ../.env

# 3. .env 파일에 카카오 API 키 입력
# KAKAO_API_KEY=your_kakao_rest_api_key_here
```

### 2. 실행

```bash
# 프로젝트 루트에서 실행
cd /Users/yonghwan/Desktop/project
python preprocessing/preprocess_stops.py
```

### 3. 결과 확인

```bash
# 전처리된 파일 확인
head data/stops_processed.csv

# Python으로 확인
python -c "import pandas as pd; df = pd.read_csv('data/stops_processed.csv'); print(df.info()); print(df.head())"
```

## 📋 모듈 설명

### `utils.py` - 공통 유틸리티

재사용 가능한 헬퍼 함수들을 제공합니다.

**주요 함수:**
- `pad_ars_id(ars_id)`: ARS_ID 제로패딩
- `extract_district(address)`: 주소에서 구 정보 추출
- `create_display_name(station_name, ars_id)`: 표시명 생성
- `is_valid_coordinate(lat, lon)`: 좌표 유효성 검증

**사용 예시:**
```python
from utils import pad_ars_id, create_display_name

# ARS_ID 패딩
padded = pad_ars_id("123")  # "00123"

# 표시명 생성
display = create_display_name("강남역", "23111")  # "강남역(23111)"
```

### `kakao_api.py` - 카카오 로컬 API

좌표를 주소로 변환하는 기능을 제공합니다.

**주요 기능:**
- 카카오 로컬 API 연동
- Rate limiting (요청 간 0.1초 대기)
- 재시도 로직 (최대 3회)
- 에러 처리 및 로깅

**사용 예시:**
```python
from kakao_api import coord_to_address, test_api_connection

# API 연결 테스트
test_api_connection()

# 좌표 → 구 이름 변환
district = coord_to_address(37.5665, 126.9780)  # "종로구"
```

### `preprocess_stops.py` - 메인 실행 파일

전체 전처리 프로세스를 실행합니다.

**주요 함수:**
- `load_data()`: CSV 로드
- `apply_ars_id_padding()`: ARS_ID 패딩
- `remove_missing_values()`: 결측치 제거
- `fill_region_names()`: region_name 채우기
- `create_display_names()`: display_name 생성
- `save_data()`: 결과 저장

## 🔑 카카오 API 키 발급

1. [카카오 개발자 사이트](https://developers.kakao.com/) 접속
2. 내 애플리케이션 > 애플리케이션 추가하기
3. 앱 설정 > 앱 키 > REST API 키 복사
4. `.env` 파일에 추가:
   ```
   KAKAO_API_KEY=your_rest_api_key_here
   ```

## ⚠️ 주의사항

- 카카오 API는 하루 호출 제한이 있습니다 (무료: 300,000회/일)
- `region_name`이 비어있는 행이 많을 경우 처리 시간이 오래 걸릴 수 있습니다
- API 호출 실패 시 해당 행의 `region_name`은 비어있는 상태로 남습니다

## 📊 예상 결과

전처리 후 `stops_processed.csv` 파일은 다음 컬럼을 포함합니다:

| 컬럼명 | 설명 | 예시 |
|--------|------|------|
| station_id | 정류소 ID | "108900216" |
| ars_id | ARS ID (5자리) | "09500" |
| station_name | 정류소명 | "우이동" |
| lat | 위도 | 37.6634309704 |
| lon | 경도 | 127.0122904688 |
| region_name | 구 이름 | "강북구" |
| display_name | 표시명 | "우이동(09500)" |

## 🐛 문제 해결

### "KAKAO_API_KEY가 설정되지 않았습니다" 오류
- `.env` 파일이 프로젝트 루트에 있는지 확인
- `.env` 파일에 `KAKAO_API_KEY=...` 형식으로 입력했는지 확인

### "입력 파일을 찾을 수 없습니다" 오류
- `data/stops.csv` 파일이 존재하는지 확인
- 프로젝트 루트 디렉토리에서 실행했는지 확인

### API 호출 실패
- 인터넷 연결 확인
- API 키가 유효한지 확인
- 일일 호출 제한을 초과하지 않았는지 확인
