import pandas as pd
import os

# 1. 파일 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
# 원본 데이터 파일명
ROUTE_STATIONS_FILE = os.path.join(current_dir, '../data/route_stations.csv')
ROUTES_FILE = os.path.join(current_dir, '../data/routes.csv')
OUTPUT_FILE = os.path.join(current_dir, '../data/route_stations_processed.csv')

def preprocess_routes():
    print("📂 노선 데이터 로딩 중...")

    if not os.path.exists(ROUTE_STATIONS_FILE):
        print(f"❌ 원본 파일을 찾을 수 없습니다: {ROUTE_STATIONS_FILE}")
        print("   data 폴더에 'route_stations.csv' 파일이 있는지 확인해주세요.")
        return

    if not os.path.exists(ROUTES_FILE):
        print(f"❌ 노선 정보 파일을 찾을 수 없습니다: {ROUTES_FILE}")
        print("   data 폴더에 'routes.csv' 파일이 있는지 확인해주세요.")
        return

    # CSV 읽기 (ID는 숫자가 훼손되지 않게 문자열로 읽기)
    df = pd.read_csv(ROUTE_STATIONS_FILE, dtype={'route_id': str, 'station_id': str, 'ars_id': str})

    # 노선 정보 로드 (버스 번호를 얻기 위함)
    routes_df = pd.read_csv(ROUTES_FILE, dtype={'route_id': str})

    # 노선 번호 병합
    df = df.merge(routes_df, on='route_id', how='left')
    
    # 컬럼명 공백 제거 (매우 중요!)
    df.columns = df.columns.str.strip()
    
    print(f"   원본 데이터: {len(df)}개 로드됨")

    # 2. 필수 컬럼만 선택 및 결측치 제거
    # 파일의 실제 컬럼명: route_id, route_no, station_id, ars_id, station_name, station_seq, lat, lon
    use_cols = ['route_id', 'route_no', 'station_seq', 'ars_id', 'station_name', 'lat', 'lon']

    # 혹시 컬럼명이 다를 경우를 대비한 방어 코드
    available_cols = [c for c in use_cols if c in df.columns]
    df = df[available_cols].copy()

    # 좌표나 순번이 없는 데이터는 삭제
    df = df.dropna(subset=['lat', 'lon', 'station_seq'])
    
    # 3. 정렬 (Sorting) - ⭐ 이 작업이 없으면 선이 꼬입니다!
    # 순번을 숫자로 변환 (문자열 '10'이 '2'보다 앞에 오는 것 방지)
    df['station_seq'] = pd.to_numeric(df['station_seq'], errors='coerce')

    # 노선별로 묶고, 그 안에서 순번대로 정렬
    df = df.sort_values(by=['route_id', 'station_seq'])
    
    # 4. 저장
    print(f"💾 정제된 데이터 저장 중... ({len(df)}개)")
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    
    print("------------------------------------------------")
    print("✅ 2차 전처리 완료!")
    print(f"   생성된 파일: {OUTPUT_FILE}")
    print("   이제 지도에 끊김 없는 노선 경로를 그릴 수 있습니다.")

if __name__ == "__main__":
    preprocess_routes()

## 🏃‍♂️ 실행 방법
#1.  **터미널(Terminal)**을 엽니다.
#2.  `project` 폴더(최상위) 위치에서 아래 명령어를 입력합니다.
#    python preprocessing/preprocess_routes.py