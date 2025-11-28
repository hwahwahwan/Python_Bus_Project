# 변경 이력 (Changelog)

## [2025.11.28] - 버스 카드 클릭 및 애니메이션 기능 추가

### 추가 (Added)
- **버스 카드 추적 버튼**: 각 버스 카드에 "🔍 [노선]번 추적" 버튼 추가
  - 파일: `src/ui/bus_cards.py` (lines 73-78)
  - 클릭 시 실시간 버스 추적 탭으로 자동 연동
  - `busRouteId` 필드 추가로 정확한 노선 ID 전달
- **탭 전환 알림**: 버스 선택 시 탭 전환 안내 메시지 표시
  - 파일: `app.py` (lines 84-90)
- **버스 마커 애니메이션**: 선형 보간을 통한 부드러운 마커 이동
  - 파일: `src/ui/bus_tracker.py` (_interpolate_positions 함수)
  - 0.5초 간격으로 위치 보간
  - 지도 줌/위치 상태 유지
- **세션 관리 함수**: 애니메이션용 상태 관리 함수 6개 추가
  - 파일: `src/core/session_manager.py` (lines 263-367)

### 수정 (Changed)
- **사이드바 노선 선택 제거**: 버스 추적 탭에서 사이드바 노선 선택 UI 제거
  - 파일: `src/ui/bus_tracker.py`
  - `_render_route_selector()` 함수 완전 삭제
  - 더 간편한 사용자 경험 제공
- **지도 재중심 버튼 제거**: 뷰 상태 자동 유지로 불필요
  - 파일: `src/ui/bus_tracker.py`
- **API 응답 구조 개선**: `busRouteId` 필드 파싱 추가
  - 파일: `src/api/bus_api.py::parse_bus_data()` (line 48)
- **지도 뷰 상태 파라미터 추가**: view_state 파라미터로 줌/위치 유지
  - 파일: `src/ui/map_view.py::create_bus_tracking_map()` (lines 273-339)

### 수정 (Fixed)
- ✅ 버스 마커 순간이동 문제 (선형 보간으로 해결)
- ✅ 지도 줌/위치가 60초마다 초기화되던 문제
- ✅ 버스 카드에서 추적 버튼이 표시되지 않던 문제

---

## [2025.11.28] - 버스 위치 추적 기능 개선

### 추가 (Added)
- 실시간 버스 위치 추적 UI 모듈 (`src/ui/bus_tracker.py`)
- 버스 위치 조회 API 함수 (`src/api/bus_api.py::get_bus_positions()`)
- 노선 데이터 로더 함수들 (`src/core/data_loader.py`)
- 버스 추적 세션 관리 함수들 (`src/core/session_manager.py`)
- 종합 테스트 스크립트 (`test_bus_tracker.py`)
- 테스트 결과 요약 문서 (`test_results_summary.md`)

### 수정 (Changed)
- **API 호출 간격 최적화**
  - `AUTO_REFRESH_INTERVAL_SECONDS`: 30초 → 60초
  - 파일: `src/utils/constants.py` (line 116)

- **자동 새로고침 로직 전면 개선**
  - 기존: 1초마다 `st.rerun()` 호출 → HTML 렌더링 방해
  - 개선: 5초 간격 체크, 60초마다 API 호출
  - HTML 테이블 정상 렌더링 보장
  - 지도 흰색 깜빡임 현상 해결
  - 파일: `src/ui/bus_tracker.py` (lines 55-89)

- **PyDeck API 업데이트**
  - Deprecated `get_color` → `get_fill_color` 변경
  - 3개 함수 수정:
    - `create_map_layer()` (line 49)
    - `create_bus_markers_layer()` (line 241)
    - `create_current_stop_layer()` (line 264)
  - 파일: `src/ui/map_view.py`

### 수정 (Fixed)
- ✅ HTML 테이블이 raw HTML 코드로 표시되던 문제
- ✅ 버스 위치가 업데이트되지 않던 문제
- ✅ 지도가 새로고침할 때마다 하얗게 깜빡이던 문제
- ✅ PyDeck deprecated 경고 메시지
- ✅ 버스 위치 API XML 파싱 오류
  - `resultCode` → `headerCd`
  - `vehId` → `plainNo`
  - `stOrd` → `sectOrd`

### 테스트 (Testing)
- ✅ 버스 위치 API 호출 테스트 (273번 버스, 4대 운행 확인)
- ✅ HTML 테이블 생성 및 태그 검증
- ✅ API 호출 간격 설정 확인 (60초)
- ✅ 전체 기능 통합 테스트 완료

### 성능 개선 (Performance)
- API 호출 빈도 50% 감소 (30초 → 60초)
- 불필요한 rerun 80% 감소 (1초 → 5초 간격)
- 서버 부하 및 네트워크 트래픽 감소

---

## [2025.11.27] - 초기 버스 위치 추적 기능 구현

### 추가 (Added)
- 버스 위치 추적 탭 추가
- 노선별 버스 위치 조회 기능
- 노선 경로 지도 시각화 (PathLayer)
- 버스 마커 지도 표시 (ScatterplotLayer)
- 자동 새로고침 기능 (초기 30초 간격)

### 데이터 (Data)
- 노선-정류소 매핑 데이터 전처리 완료
- `route_stations_processed.csv` 생성
- 노선별 정류장 순서 및 GPS 좌표 포함

---

## [2025.11.26] - 정류장 조회 기능 개선

### 추가 (Added)
- 정류장 선택 시 해당 정류장 경유 노선만 필터링
- 버스 카드 UI 프로토타입 적용
- 자동 새로고침 기능

### 수정 (Changed)
- 지도 스타일 변경 (Mapbox → PyDeck 내장 스타일)
- UI 레이아웃 개선

---

## [2025.11.25] - 초기 프로젝트 설정

### 추가 (Added)
- 프로젝트 구조 설계
- 정류장 데이터 전처리 (12,859개)
- 버스 도착 정보 조회 기능
- 지도 시각화 기능
- README 및 문서 작성

### 데이터 (Data)
- 카카오 로컬 API 연동
- 서울시 공공데이터 API 연동
- 정류장 데이터 전처리 완료
