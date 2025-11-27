"""
버스 추적 기능 테스트 스크립트

이 스크립트는 다음을 테스트합니다:
1. 버스 위치 API 호출
2. HTML 테이블 생성
3. 데이터 파싱
"""

from src.api.bus_api import get_bus_positions
from src.core.data_loader import get_route_id_by_number

def test_bus_position_api():
    """버스 위치 API 테스트"""
    print("=" * 60)
    print("1. 버스 위치 API 테스트")
    print("=" * 60)

    # 273번 버스 route_id
    route_id = "100100124"
    route_name = "273"

    print(f"노선: {route_name} (ID: {route_id})")
    print("-" * 60)

    result = get_bus_positions(route_id)

    if result["success"]:
        print(f"✅ API 호출 성공!")
        print(f"운행 중인 버스: {len(result['data'])}대\n")

        for idx, bus in enumerate(result['data'], start=1):
            print(f"버스 #{idx}")
            print(f"  - 차량번호: {bus.get('vehicle_no', 'N/A')}")
            print(f"  - 정류장 순서: {bus.get('station_seq', 0)}번째")
            print(f"  - 현재 위치: {bus.get('station_name', 'N/A')}")
            print(f"  - 위도/경도: {bus.get('lat', 0):.6f}, {bus.get('lon', 0):.6f}")
            print(f"  - 혼잡도: {bus.get('congestion', '정보없음')}")
            print(f"  - 버스 타입: {bus.get('bus_type', '0')}")
            print()
    else:
        print(f"❌ API 호출 실패: {result.get('error_message', '알 수 없는 오류')}")

    return result

def test_html_table_generation(bus_positions):
    """HTML 테이블 생성 테스트"""
    print("=" * 60)
    print("2. HTML 테이블 생성 테스트")
    print("=" * 60)

    if not bus_positions:
        print("⚠️ 버스 위치 데이터가 없습니다.")
        return

    # HTML 테이블 생성 로직 (bus_tracker.py와 동일)
    table_html = """
    <style>
    .bus-table {
        width: 100%;
        border-collapse: collapse;
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        table-layout: fixed;
    }
    .bus-table th {
        background: #f8f9fa;
        text-align: center;
        padding: 12px;
        font-size: 0.9rem;
        color: #555;
        border-bottom: 2px solid #eee;
    }
    .bus-table td {
        padding: 10px;
        border-top: 1px solid #eee;
        font-size: 0.9rem;
        text-align: center;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .coord-text {
        font-family: 'Courier New', Courier, monospace;
        color: #666;
        font-size: 0.85rem;
    }
    .badge {
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .bg-low {
        background: #e3f2fd;
        color: #1565c0;
    }
    .bg-normal {
        background: #f5f5f5;
        color: #616161;
    }
    </style>
    <table class="bus-table">
        <colgroup>
            <col style="width: 8%">
            <col style="width: 15%">
            <col style="width: 10%">
            <col style="width: 22%">
            <col style="width: 15%">
            <col style="width: 15%">
            <col style="width: 15%">
        </colgroup>
        <thead>
            <tr>
                <th>순번</th>
                <th>차량번호</th>
                <th>유형</th>
                <th>현재 위치</th>
                <th>혼잡도</th>
                <th>위도</th>
                <th>경도</th>
            </tr>
        </thead>
        <tbody>
    """

    for idx, bus in enumerate(bus_positions, start=1):
        bus_type = "저상" if bus.get("bus_type") == "1" else "일반"
        badge_class = "bg-low" if bus.get("bus_type") == "1" else "bg-normal"

        table_html += f"""
            <tr>
                <td>{idx}</td>
                <td style="font-weight: bold;">{bus.get('vehicle_no', 'N/A')}</td>
                <td><span class="badge {badge_class}">{bus_type}</span></td>
                <td>{bus.get('station_name', 'N/A')} {bus.get('station_seq', 0)}번째</td>
                <td>{bus.get('congestion', '정보없음')}</td>
                <td class="coord-text">{bus.get('lat', 0):.6f}</td>
                <td class="coord-text">{bus.get('lon', 0):.6f}</td>
            </tr>
        """

    table_html += """
        </tbody>
    </table>
    """

    print(f"✅ HTML 테이블 생성 완료!")
    print(f"HTML 길이: {len(table_html)} 문자")
    print(f"테이블 행 수: {len(bus_positions)}")

    # HTML 구조 검증
    if "<table" in table_html and "</table>" in table_html:
        print("✅ HTML 테이블 태그 정상")
    else:
        print("❌ HTML 테이블 태그 누락")

    if table_html.count("<tr>") == table_html.count("</tr>"):
        print(f"✅ <tr> 태그 정상 ({table_html.count('<tr>')}개)")
    else:
        print("❌ <tr> 태그 불일치")

    if table_html.count("<td>") == table_html.count("</td>"):
        print(f"✅ <td> 태그 정상 ({table_html.count('<td>')}개)")
    else:
        print("❌ <td> 태그 불일치")

    print()

def test_auto_refresh_settings():
    """자동 새로고침 설정 테스트"""
    print("=" * 60)
    print("3. 자동 새로고침 설정 테스트")
    print("=" * 60)

    from src.utils.constants import AUTO_REFRESH_INTERVAL_SECONDS

    print(f"자동 새로고침 간격: {AUTO_REFRESH_INTERVAL_SECONDS}초")

    if AUTO_REFRESH_INTERVAL_SECONDS == 60:
        print("✅ API 호출 간격이 60초로 설정되어 있습니다.")
    else:
        print(f"⚠️ API 호출 간격이 {AUTO_REFRESH_INTERVAL_SECONDS}초입니다. (권장: 60초)")

    print()

if __name__ == "__main__":
    print("\n🧪 버스 추적 기능 테스트 시작\n")

    # 테스트 1: API 호출
    result = test_bus_position_api()

    # 테스트 2: HTML 테이블 생성
    if result["success"] and result["data"]:
        test_html_table_generation(result["data"])

    # 테스트 3: 설정 확인
    test_auto_refresh_settings()

    print("=" * 60)
    print("🎉 모든 테스트 완료!")
    print("=" * 60)
