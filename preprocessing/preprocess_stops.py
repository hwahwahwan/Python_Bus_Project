"""
버스 정류소 데이터 전처리 메인 스크립트

이 스크립트는 stops.csv 파일을 읽어서 다음 작업을 수행합니다:
1. ID를 문자열로 강제 변환
2. ARS_ID 제로패딩 (5자리)
3. 결측치 및 이상치 제거
4. region_name 빈 값 채우기 (카카오 API 사용)
5. display_name 컬럼 생성
6. 전처리된 데이터 저장

사용법:
    python preprocessing/preprocess_stops.py
"""

import os
import sys
import pandas as pd
from pathlib import Path

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from utils import pad_ars_id, create_display_name, is_valid_coordinate
from kakao_api import coord_to_address, test_api_connection

# 파일 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
INPUT_FILE = DATA_DIR / 'stops.csv'
OUTPUT_FILE = DATA_DIR / 'stops_processed.csv'


def load_data() -> pd.DataFrame:
    """
    CSV 파일을 로드하고 ID를 문자열로 강제 변환합니다.
    
    Returns:
        pd.DataFrame: 로드된 데이터프레임
    """
    print("📂 데이터 로드 중...")
    print(f"   파일: {INPUT_FILE}")
    
    # ID를 문자열로 강제 변환
    df = pd.read_csv(
        INPUT_FILE,
        dtype={
            'station_id': str,
            'ars_id': str
        }
    )
    
    print(f"✅ 데이터 로드 완료: {len(df):,}개 행")
    return df


def apply_ars_id_padding(df: pd.DataFrame) -> pd.DataFrame:
    """
    ARS_ID를 5자리로 제로패딩합니다.
    
    Args:
        df (pd.DataFrame): 원본 데이터프레임
        
    Returns:
        pd.DataFrame: 패딩이 적용된 데이터프레임
    """
    print("\n🔢 ARS_ID 제로패딩 적용 중...")
    
    # 패딩 전 샘플 출력
    print(f"   패딩 전 샘플: {df['ars_id'].head(3).tolist()}")
    
    df['ars_id'] = df['ars_id'].apply(pad_ars_id)
    
    # 패딩 후 샘플 출력
    print(f"   패딩 후 샘플: {df['ars_id'].head(3).tolist()}")
    print("✅ ARS_ID 제로패딩 완료")
    
    return df


def remove_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    결측치 및 이상치를 제거합니다.
    
    Args:
        df (pd.DataFrame): 원본 데이터프레임
        
    Returns:
        pd.DataFrame: 정제된 데이터프레임
    """
    print("\n🧹 결측치 및 이상치 제거 중...")
    
    initial_count = len(df)
    
    # 1. 좌표 또는 정류소명이 NULL인 행 제거
    df = df.dropna(subset=['lat', 'lon', 'station_name'])
    after_null = len(df)
    removed_null = initial_count - after_null
    
    if removed_null > 0:
        print(f"   - NULL 값 제거: {removed_null:,}개 행")
    
    # 2. 유효하지 않은 좌표 제거 (0이거나 범위를 벗어난 경우)
    df = df[df.apply(lambda row: is_valid_coordinate(row['lat'], row['lon']), axis=1)]
    after_invalid = len(df)
    removed_invalid = after_null - after_invalid
    
    if removed_invalid > 0:
        print(f"   - 유효하지 않은 좌표 제거: {removed_invalid:,}개 행")
    
    total_removed = initial_count - after_invalid
    print(f"✅ 총 {total_removed:,}개 행 제거됨 (남은 행: {after_invalid:,}개)")
    
    return df


def remove_missing_region_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    region_name이 비어있는 행을 제거합니다.
    
    Args:
        df (pd.DataFrame): 원본 데이터프레임
        
    Returns:
        pd.DataFrame: region_name이 채워진 데이터프레임
    """
    print("\n🗑️  region_name 비어있는 행 제거 중...")
    
    initial_count = len(df)
    
    # region_name이 비어있는 행 제거
    df = df.dropna(subset=['region_name'])
    after_removal = len(df)
    removed_count = initial_count - after_removal
    
    if removed_count > 0:
        print(f"   - region_name 비어있는 행 제거: {removed_count:,}개")
    else:
        print(f"   - 제거할 행 없음 (모든 행에 region_name 존재)")
    
    print(f"✅ 남은 행: {after_removal:,}개")
    
    return df


def fill_region_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    region_name이 비어있는 행에 대해 카카오 API로 주소를 조회하여 채웁니다.
    
    Args:
        df (pd.DataFrame): 원본 데이터프레임
        
    Returns:
        pd.DataFrame: region_name이 채워진 데이터프레임
    """
    print("\n🗺️  region_name 채우기 중...")
    
    # region_name이 비어있는 행 찾기
    missing_mask = df['region_name'].isna()
    missing_count = missing_mask.sum()
    
    if missing_count == 0:
        print("✅ 모든 행에 region_name이 이미 존재합니다.")
        return df
    
    print(f"   - region_name이 비어있는 행: {missing_count:,}개")
    print("   - 카카오 API로 주소 조회 시작...")
    
    # API 연결 테스트
    if not test_api_connection():
        print("❌ 카카오 API 연결 실패. region_name 채우기를 건너뜁니다.")
        return df
    
    # 비어있는 행에 대해 API 호출
    filled_count = 0
    failed_count = 0
    
    for idx in df[missing_mask].index:
        lat = df.loc[idx, 'lat']
        lon = df.loc[idx, 'lon']
        station_name = df.loc[idx, 'station_name']
        
        print(f"   [{filled_count + failed_count + 1}/{missing_count}] {station_name} ({lat}, {lon})")
        
        district = coord_to_address(lat, lon)
        
        if district:
            df.loc[idx, 'region_name'] = district
            filled_count += 1
            print(f"      ✅ {district}")
        else:
            failed_count += 1
            print(f"      ❌ 실패")
    
    print(f"\n✅ region_name 채우기 완료:")
    print(f"   - 성공: {filled_count:,}개")
    print(f"   - 실패: {failed_count:,}개")
    
    return df


def create_display_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    display_name 컬럼을 생성합니다 (정류소명 + ARS_ID).
    
    Args:
        df (pd.DataFrame): 원본 데이터프레임
        
    Returns:
        pd.DataFrame: display_name 컬럼이 추가된 데이터프레임
    """
    print("\n🏷️  display_name 컬럼 생성 중...")
    
    df['display_name'] = df.apply(
        lambda row: create_display_name(row['station_name'], row['ars_id']),
        axis=1
    )
    
    # 샘플 출력
    print(f"   샘플: {df['display_name'].head(3).tolist()}")
    print("✅ display_name 컬럼 생성 완료")
    
    return df


def save_data(df: pd.DataFrame) -> None:
    """
    전처리된 데이터를 CSV 파일로 저장합니다.
    
    Args:
        df (pd.DataFrame): 저장할 데이터프레임
    """
    print(f"\n💾 데이터 저장 중...")
    print(f"   파일: {OUTPUT_FILE}")
    
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    
    print(f"✅ 저장 완료: {len(df):,}개 행")


def print_summary(df: pd.DataFrame) -> None:
    """
    전처리 결과 요약을 출력합니다.
    
    Args:
        df (pd.DataFrame): 전처리된 데이터프레임
    """
    print("\n" + "="*60)
    print("📊 전처리 결과 요약")
    print("="*60)
    print(f"총 행 수: {len(df):,}개")
    print(f"총 컬럼 수: {len(df.columns)}개")
    print(f"\n컬럼 목록:")
    for col in df.columns:
        print(f"  - {col}")
    
    print(f"\nregion_name 통계:")
    region_counts = df['region_name'].value_counts()
    print(f"  - 고유한 구 개수: {len(region_counts)}개")
    print(f"  - 상위 5개 구:")
    for region, count in region_counts.head(5).items():
        print(f"    • {region}: {count:,}개")
    
    print("="*60)


def main():
    """
    메인 실행 함수
    """
    print("\n" + "="*60)
    print("🚌 버스 정류소 데이터 전처리 시작")
    print("="*60)
    
    try:
        # 1. 데이터 로드
        df = load_data()
        
        # 2. ARS_ID 제로패딩
        df = apply_ars_id_padding(df)
        
        # 3. 결측치 및 이상치 제거
        df = remove_missing_values(df)
        
        # 4. region_name 채우기
        df = fill_region_names(df)
        
        # 5. region_name 비어있는 행 제거
        df = remove_missing_region_names(df)
        
        # 6. display_name 생성
        df = create_display_names(df)
        
        # 7. 데이터 저장
        save_data(df)
        
        # 7. 결과 요약
        print_summary(df)
        
        print("\n✅ 전처리 완료!")
        print(f"   결과 파일: {OUTPUT_FILE}")
        
    except FileNotFoundError:
        print(f"\n❌ 오류: 입력 파일을 찾을 수 없습니다: {INPUT_FILE}")
        print("   data/stops.csv 파일이 존재하는지 확인해주세요.")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
