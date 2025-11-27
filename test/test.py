import streamlit as st
import pandas as pd
import pydeck as pdk
import os

# 1. 페이지 설정 (반드시 가장 윗줄에 있어야 함)
st.set_page_config(layout="wide", page_title="버스 정류장 데이터 테스트")

# 2. 데이터 경로 설정 (자동 감지)
current_dir = os.path.dirname(os.path.abspath(__file__)) # .../project/test/
root_dir = os.path.dirname(current_dir)                # .../project/
DATA_PATH = os.path.join(root_dir, 'data', 'stops_processed.csv')

# 3. 데이터 로드 함수
@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        st.error(f"❌ 데이터 파일을 찾을 수 없습니다!\n경로: {DATA_PATH}")
        return pd.DataFrame()

    # CSV 읽기
    # ars_id는 '09500'처럼 앞의 0을 유지해야 하므로 문자열(str)로 읽습니다.
    df = pd.read_csv(DATA_PATH, dtype={'ars_id': str, 'station_id': str})
    
    # 컬럼명 공백 제거 (안전장치)
    df.columns = df.columns.str.strip()
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터 로드 중 에러 발생: {e}")
    st.stop()

# 4. 앱 UI 시작
st.title("🚏 버스 정류장 데이터 테스트 (최종)")

if df.empty:
    st.warning("데이터가 비어있습니다. 전처리 파일을 확인해주세요.")
    st.stop()

# --- 상단 필터 (지역 -> 정류장) ---
col1, col2 = st.columns([1, 3])

with col1:
    # 'region_name' (구) 컬럼 사용
    if 'region_name' in df.columns:
        gu_list = sorted(df['region_name'].unique())
        selected_gu = st.selectbox("지역(구) 선택", gu_list)
    else:
        st.error("CSV 파일에 'region_name' 컬럼이 없습니다.")
        st.stop()

with col2:
    # 선택된 구의 정류장만 필터링
    filtered_df = df[df['region_name'] == selected_gu]
    
    # 'display_name' (우이동(09500)) 컬럼 사용
    if 'display_name' in filtered_df.columns:
        stop_list = filtered_df['display_name'].tolist()
        selected_stop_str = st.selectbox("정류장 선택", stop_list)
    else:
        st.error("CSV 파일에 'display_name' 컬럼이 없습니다.")
        st.stop()

# --- 선택된 정류장 데이터 찾기 ---
if not selected_stop_str:
    st.stop()

# display_name이 일치하는 행 찾기
match_rows = filtered_df[filtered_df['display_name'] == selected_stop_str]

if match_rows.empty:
    st.error(f"데이터 매칭 실패: {selected_stop_str}")
    st.stop()

# 첫 번째 결과 가져오기
target_stop = match_rows.iloc[0]

# --- 하단 지도 및 정보 영역 ---
st.divider()
map_col, info_col = st.columns([2, 1])

with map_col:
    st.subheader(f"📍 {target_stop['station_name']} 위치")
    
    # PyDeck 지도 설정
    # lat: 위도, lon: 경도
    view_state = pdk.ViewState(
        latitude=target_stop['lat'], 
        longitude=target_stop['lon'],
        zoom=15,
        pitch=0
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=pd.DataFrame([target_stop]),
        get_position='[lon, lat]',  # PyDeck은 [경도, 위도] 순서입니다.
        get_color='[0, 100, 255, 200]', # 파란색
        get_radius=50,
        pickable=True
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "{station_name}\n({ars_id})"}
    ))

with info_col:
    st.subheader("상세 정보")
    # CSV 컬럼명에 맞춰서 데이터 표시
    st.write(f"- **정류장명:** {target_stop['station_name']}")
    st.write(f"- **ARS-ID:** {target_stop['ars_id']}")
    st.write(f"- **Station-ID:** {target_stop['station_id']}")
    st.write(f"- **지역:** {target_stop['region_name']}")
    st.code(f"좌표: {target_stop['lat']}, {target_stop['lon']}")
    
    st.info("✅ 데이터가 정상적으로 연결되었습니다.")