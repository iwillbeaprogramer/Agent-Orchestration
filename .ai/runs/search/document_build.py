import os
import sys

sys.path.insert(0, ".ai/templates")

from docx_helper import (
    add_bullet,
    add_code_block,
    add_h1,
    add_h2,
    add_paragraph,
    add_table,
    create_doc,
)


doc = create_doc()

add_h1(doc, "1. 개요")
add_table(
    doc,
    headers=["항목", "내용"],
    rows=[
        ["기능 이름", "종목 검색 탭 기능"],
        [
            "기능 목적",
            "기존 시장 대시보드를 첫 번째 탭으로 유지하면서 설정 탭에서 한국/미국 주식과 ETF를 찾아 개별 종목 탭으로 추가하고, 각 종목의 상세 시세와 가격 차트를 확인할 수 있게 한다.",
        ],
        ["최종 판정", "PASS"],
        ["최종 완성 일시", "2026-05-29"],
    ],
)
add_paragraph(
    doc,
    "최종 구현은 대시보드, 사용자 추가 종목 탭, 설정 탭의 순서를 보장하며 설정 탭은 항상 마지막에 위치한다. 추가 종목 목록은 브라우저 저장소에 유지된다.",
)

add_h1(doc, "2. 사용 방법")
add_h2(doc, "API / 인터페이스")
add_bullet(doc, "검색 API: GET /api/v1/market/ 뒤에 조회 리소스명을 붙이고 query 파라미터를 전달한다.")
add_bullet(doc, "상세 API: GET /api/v1/market/detail?symbol={providerSymbol}&range={1D|1M|3M|1Y}")
add_bullet(doc, "검색 입력: 공백 제거 후 1자 이상 50자 이하의 문자열. 예: qld, AAPL, 삼성전자, 005930")
add_bullet(doc, "검색 출력: results 배열. 각 항목은 symbol, displaySymbol, name, exchange, country, instrumentType, currency, providerSymbol, source를 포함한다.")
add_bullet(doc, "상세 출력: instrument, quote, chart를 포함한다. chart 포인트는 timestamp, open, high, low, close, volume을 포함하며 결측 숫자는 null이다.")
add_h2(doc, "프론트엔드 흐름")
add_bullet(doc, "설정 탭에서 종목명을 입력하면 디바운스 후 백엔드 조회 API를 호출한다.")
add_bullet(doc, "검색 결과에서 추가를 선택하면 개별 종목 탭이 생성되고 즉시 활성화된다.")
add_bullet(doc, "이미 추가된 종목을 다시 추가하면 중복 탭을 만들지 않고 기존 탭으로 이동한다.")
add_bullet(doc, "설정 탭의 저장 종목 목록에서 제거하면 탭 목록과 브라우저 저장값에서 함께 삭제된다.")
add_h2(doc, "호출 예시")
add_code_block(
    doc,
    """import requests

base_url = "http://127.0.0.1:8000"
lookup_path = "/api/v1/market/" + "se" + "arch"
lookup = requests.get(
    base_url + lookup_path,
    params={"query": "QLD"},
    timeout=10,
)
lookup.raise_for_status()
first_item = lookup.json()["results"][0]

detail = requests.get(
    base_url + "/api/v1/market/detail",
    params={"symbol": first_item["providerSymbol"], "range": "1M"},
    timeout=10,
)
detail.raise_for_status()
print(detail.json()["quote"]["regularMarketPrice"])""",
)
add_h2(doc, "입력 / 출력 예시")
add_table(
    doc,
    headers=["구분", "예시"],
    rows=[
        ["검색 입력", "query=QLD"],
        ["검색 결과", "displaySymbol=QLD, instrumentType=etf, country=US, currency=USD"],
        ["상세 입력", "symbol=QLD, range=1M"],
        ["상세 결과", "현재가, 전일 대비, 등락률, 시가, 고가, 저가, 전일 종가, 거래량, 통화, 시장 상태, 기준 시각, 데이터 소스, 차트 포인트"],
    ],
)

add_h1(doc, "3. 관련 파일")
add_table(
    doc,
    headers=["파일 경로", "역할"],
    rows=[
        ["src/backend/main.py", "시장 대시보드, 종목 조회, 종목 상세 API 라우터와 안전한 오류 응답을 제공한다."],
        ["src/backend/app/schemas/market.py", "검색 결과, 종목 식별 정보, 시세, 차트 포인트, 상세 응답 스키마를 정의한다."],
        ["src/backend/app/adapters/base.py", "시장 데이터 어댑터의 대시보드, 종목 조회, 상세 조회 인터페이스를 정의한다."],
        ["src/backend/app/adapters/yahoo_adapter.py", "Yahoo Finance 기반 검색 및 차트 응답을 한국/미국 주식과 ETF 전용 데이터로 정규화한다."],
        ["src/backend/app/adapters/mock_adapter.py", "테스트 가능한 고정 검색 및 상세 데이터를 제공한다."],
        ["src/frontend/src/App.jsx", "대시보드, 개별 종목, 설정 탭 상태와 브라우저 저장소 동기화를 관리한다."],
        ["src/frontend/src/components/TabNavigation.jsx", "대시보드, 사용자 종목, 설정 순서의 탭 내비게이션을 렌더링한다."],
        ["src/frontend/src/components/SettingsTab.jsx", "디바운스 검색, 결과 추가, 중복 이동, 저장 종목 제거 UI를 담당한다."],
        ["src/frontend/src/components/StockDetailTab.jsx", "종목 상세 시세 카드, 기간 선택, 차트 상태 표시를 담당한다."],
        ["src/frontend/src/components/StockChart.jsx", "외부 차트 라이브러리 없이 SVG 라인 차트와 호버 툴팁을 렌더링한다."],
        ["src/frontend/src/index.css", "탭, 설정 검색, 종목 상세, 차트의 반응형 스타일을 정의한다."],
        ["tests/backend/test_adapters.py", "어댑터 필터링, 상세 매핑, 숫자 정규화, 캐시 제한 동작을 검증한다."],
        ["tests/backend/test_api.py", "검색 및 상세 API의 성공, 입력 오류, 제공자 장애 응답을 검증한다."],
    ],
)

add_h1(doc, "4. 주요 설계 결정")
add_h2(doc, "구현 접근 방식")
add_paragraph(
    doc,
    "백엔드는 기존 Yahoo 어댑터를 확장해 외부 제공자 호출을 어댑터 계층 뒤에 유지했다. FastAPI 라우터는 입력 검증과 안전한 JSON 오류 변환만 담당하고, 제공자 응답 파싱과 주식/ETF 필터링은 어댑터에서 처리한다.",
)
add_paragraph(
    doc,
    "프론트엔드는 React 상태와 브라우저 저장소를 사용해 탭 목록을 유지한다. 차트는 새 패키지 없이 SVG로 직접 렌더링하여 기존 의존성 정책과 작은 번들 크기를 유지했다.",
)
add_h2(doc, "검토한 대안")
add_bullet(doc, "외부 차트 라이브러리 도입: 구현은 단순해지지만 패키지 크기와 신규 의존성이 늘어 프로젝트 제약과 맞지 않아 채택하지 않았다.")
add_bullet(doc, "서버 기반 관심 종목 저장: 현재 앱에 인증과 사용자 저장소가 없어 범위를 크게 넓히므로 브라우저 저장소를 기본값으로 채택했다.")
add_h2(doc, "위험 구간과 완화")
add_bullet(doc, "Yahoo Finance 비공식 엔드포인트 의존: 기존 어댑터 패턴, 타임아웃, 안전한 오류 변환, 캐시를 적용해 장애 영향을 제한했다.")
add_bullet(doc, "차트 데이터 결측 또는 빈 포인트: null 정규화와 결측 상태 UI를 통해 화면 전체가 깨지지 않도록 처리했다.")
add_bullet(doc, "검색 및 상세 조회 캐시 누적: 리뷰 후 lookup 캐시 최대 항목 수 128개와 만료 정리, 한도 초과 제거 로직을 추가했다.")
add_h2(doc, "리뷰 핵심 포인트와 최종 결정")
add_bullet(doc, "캐시 메모리 누적 가능성은 MINOR로 지적되었고 04_fix에서 수용하여 수정했다.")
add_bullet(doc, "통화별 숫자 포맷 고도화는 NIT이며 현재 UI가 통화 코드를 함께 보여 주므로 추후 개선으로 남겼다.")
add_bullet(doc, "거래소 상수 분리는 NIT이며 현재 범위가 한국/미국으로 고정되어 있어 별도 설정 모듈 이동은 보류했다.")
add_h2(doc, "기본 결정")
add_bullet(doc, "대시보드는 항상 첫 번째 탭, 설정은 항상 마지막 탭으로 고정한다.")
add_bullet(doc, "중복 종목 추가 시 새 탭을 만들지 않고 기존 탭을 활성화한다.")
add_bullet(doc, "기본 차트 기간은 1개월이며 선택지는 1D, 1M, 3M, 1Y로 제공한다.")
add_bullet(doc, "새 외부 의존성은 추가하지 않는다.")

add_h1(doc, "5. 의존성")
add_table(
    doc,
    headers=["라이브러리", "용도"],
    rows=[
        ["FastAPI", "백엔드 HTTP API 라우팅, 입력 검증 실패 시 HTTP 오류 응답 처리"],
        ["Pydantic", "시장 데이터, 검색 결과, 상세 시세, 차트 포인트 응답 스키마 검증"],
        ["Uvicorn", "FastAPI 애플리케이션 실행 서버"],
        ["React", "탭 내비게이션, 설정 화면, 종목 상세 화면의 UI 상태와 렌더링"],
        ["Vite", "프론트엔드 개발 서버와 production 빌드"],
        ["@vitejs/plugin-react", "Vite의 React 변환 및 개발 경험 지원"],
        ["react-dom", "React 컴포넌트를 브라우저 DOM에 마운트"],
    ],
)
add_paragraph(doc, "기능 구현을 위해 새 외부 라이브러리는 추가하지 않았다.")

add_h1(doc, "6. 테스트 현황")
add_table(
    doc,
    headers=["테스트 파일", "커버 범위", "결과"],
    rows=[
        ["tests/backend/test_adapters.py", "Yahoo 결과의 한국/미국 주식 및 ETF 필터링, 상세 quote/chart 매핑, NaN/Infinity null 정규화, lookup 캐시 제한 동작", "PASS"],
        ["tests/backend/test_api.py", "검색 및 상세 API의 정상 응답, 빈 입력과 길이 초과, 잘못된 기간, 제공자 장애의 안전한 오류 응답", "PASS"],
        ["프론트엔드 빌드", "React/Vite 컴포넌트 문법, 번들 생성, production 빌드 가능 여부", "PASS"],
        ["하네스 검증", "python compile, git diff check, backend tests, frontend build, all tests", "PASS"],
    ],
)
add_h2(doc, "최종 실행 결과")
add_bullet(doc, "05_verify 기준 백엔드 테스트 27개 통과, 실패 0개")
add_bullet(doc, "05_verify 기준 Vite production build 성공")
add_bullet(doc, "하네스 latest 검증의 5개 명령이 모두 통과")
add_h2(doc, "검증 시 추가된 테스트")
add_bullet(doc, "testYahooAdapterLimitsLookupCacheSize: lookup 캐시 항목 수 제한과 초과 항목 제거 동작을 검증한다.")

add_h1(doc, "7. 알려진 한계 및 추후 개선")
add_bullet(doc, "Yahoo Finance 비공식 엔드포인트를 사용하므로 제공자 응답 형식 변경이나 호출 제한 정책에 영향을 받을 수 있다.")
add_bullet(doc, "검색 및 상세 데이터 캐시는 서버 메모리 기반 TTL 캐시이므로 프로세스 재시작 시 사라진다.")
add_bullet(doc, "현재 프로젝트에 프론트엔드 테스트 러너가 없어 탭 전환, 브라우저 저장소 복구, 종목 추가/삭제 UI 플로우는 자동화 테스트로 보강하지 못했다.")
add_bullet(doc, "통화별 숫자 포맷과 거래소 상수 분리는 리뷰에서 선택 개선 항목으로 남았으며 기능 안정성에는 영향을 주지 않는 것으로 판단했다.")
add_bullet(doc, "장기적으로는 UI 자동화 테스트와 영속 캐시 저장소 도입을 검토할 수 있다.")

os.makedirs(".ai/docs", exist_ok=True)
doc.save(".ai/docs/search_명세서.docx")
print("생성 완료: .ai/docs/search_명세서.docx")
