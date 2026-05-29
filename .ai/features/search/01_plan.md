# 01_plan - search

작성: Antigravity
일시: 2026-05-28

## 기능 목표
- 기존의 시장 대시보드를 첫 번째 탭으로 고정하고, 설정 탭을 항상 마지막 탭으로 위치시킨다.
- 사용자는 설정 탭에서 한국/미국 주식 및 ETF를 검색하여 개별 종목 전용 탭으로 추가할 수 있다.
- 추가된 개별 종목 탭에서는 상세 시세 정보(현재가, 전일비, 등락률, 시가/고가/저가/종가, 거래량 등)와 SVG 기반 자체 렌더링된 가격 차트(1D, 1M, 3M, 1Y 기간)를 제공한다.
- 추가된 종목 상태는 브라우저 `localStorage`에 유지되어 새로고침 후에도 유지되도록 한다.

## 구현 접근 방식
- **백엔드**: 기존 `YahooMarketDataAdapter`를 확장하여 Yahoo Finance 검색 API(`.../v1/finance/search`)와 차트 API(`.../v8/finance/chart/{symbol}`)를 연동한다. 차트 API는 상세 시세(`meta`)와 가격 이력(`timestamp`, `indicators`)을 한 번에 제공하므로 단일 호출로 효율적으로 처리한다.
- **프론트엔드**: React 상태 관리(`activeTab`, `customTabs`)와 `localStorage` 동기화를 활용해 유연한 탭 내비게이션을 구축한다. SVG 기반 자체 렌더링 인터랙티브 차트(호버 툴팁 포함)를 추가해 외부 라이브러리 의존성을 없애고 성능을 최적화한다.

## 검토한 대안
- **대안 1 (채택): Yahoo Finance API를 통해 주식/ETF 검색 및 상세/차트를 한 번에 조회. SVG 자체 차트 렌더링.**
  - 장점: 외부 의존성이 없고, 기존 어댑터 구조에 자연스럽게 녹아들며, 성능이 매우 빠르고 리소스가 적게 듦.
  - 단점: SVG 차트의 드로잉 및 툴팁 인터랙션을 직접 구현해야 하므로 프론트엔드 구현 코드가 다소 늘어남.
- **대안 2 (탈락): Chart.js 또는 Recharts 같은 외부 차트 라이브러리 도입.**
  - 장점: 차트 구현이 간편함.
  - 단점: 프론트엔드 패키지 크기가 늘어나며, `Project Contract`의 "외부 의존성 추가 금지 및 최소화" 제약에 어긋나 위험도가 올라감. 채택하지 않음.

## 변경 파일 계획
- **src/backend/app/schemas/market.py (수정)**: `SearchResultItem`, `SearchResponse`, `StockInstrumentInfo`, `StockQuote`, `ChartPoint`, `StockDetailResponse` Pydantic 스키마 추가.
- **src/backend/app/adapters/base.py (수정)**: `search_symbols(query)`, `get_stock_detail(symbol, range_str)` 추상 메서드 명세 추가.
- **src/backend/app/adapters/yahoo_adapter.py (수정)**: Yahoo Search & Chart API 호출 및 파싱 로직 구현. 한국/미국 주식 및 ETF만 허용하는 필터링 정책, NaN/Infinity의 `None` 정규화 처리.
- **src/backend/app/adapters/mock_adapter.py (수정)**: 테스트 및 mock용 검색, 상세 및 기간별 차트 mock 데이터 제공 구현.
- **src/backend/main.py (수정)**: `/api/v1/market/search`, `/api/v1/market/detail` GET API 라우터 구현 및 입력 유효성 검사, 예외 처리.
- **src/frontend/src/App.jsx (수정)**: 탭 상태, `customTabs` 상태(`localStorage` 연동), 화면별 조건부 렌더링.
- **src/frontend/src/index.css (수정)**: 탭 내비게이션, 설정 탭, 종목 상세 그리드, SVG 차트 및 반응형/호버 툴팁 CSS 스타일링.
- **src/frontend/src/components/TabNavigation.jsx (신규)**: 세련된 탭 내비게이션 컴포넌트.
- **src/frontend/src/components/SettingsTab.jsx (신규)**: 디바운스된 종목 검색 창, 한국/미국 주식 및 ETF 전용 검색 결과 카드, 추가/삭제 관리 기능.
- **src/frontend/src/components/StockDetailTab.jsx (신규)**: 시가/종가/고가/저가/거래량 상세 시세 그리드, 기간 선택(`1D`, `1M`, `3M`, `1Y`) 버튼, 자체 SVG 차트 컨테이너 및 상태 배너 결합.
- **src/frontend/src/components/StockChart.jsx (신규)**: SVG 라인을 그리고 호버 시 가격/시간을 보여주는 툴팁 인터랙티브 차트 컴포넌트.
- **tests/backend/test_adapters.py (수정)**: 신규 어댑터 기능의 단위 테스트 작성 (정상 경로, 예외 경로, NaN 정규화 검증).
- **tests/backend/test_api.py (수정)**: `/api/v1/market/search` 및 `/api/v1/market/detail` API 엔드포인트의 통합 테스트 작성.

## 데이터 / 제어 흐름
- **검색 흐름**:
  사용자 입력 -> SettingsTab(Debounce 300ms) -> GET /api/v1/market/search?query=... -> Yahoo Search API -> 주식/ETF 필터링, 한국/미국 정규화 -> JSON 응답 -> 프론트엔드 UI 렌더링
- **상세 및 차트 흐름**:
  탭 활성화 / 기간 클릭 -> GET /api/v1/market/detail?symbol=...&range=... -> Yahoo Chart API -> 수치 NaN 정규화 및 포인트 매핑 -> JSON 응답 -> StockDetailTab (SVG 자체 렌더링 및 툴팁 바인딩)

## 구현 단계 분할
1. **단계 1: 백엔드 스키마 및 어댑터 구현**
   - 파일: `schemas/market.py`, `adapters/base.py`, `adapters/yahoo_adapter.py`, `adapters/mock_adapter.py`
   - 완료 기준: Yahoo Finance API 호출을 연동하고 주식/ETF 필터링 및 통화/국가 기본값 매핑이 정상 작동하는 단위 테스트 통과.
2. **단계 2: 백엔드 API 라우터 구현 및 테스트**
   - 파일: `main.py`, `tests/backend/test_adapters.py`, `tests/backend/test_api.py`
   - 완료 기준: `/api/v1/market/search`와 `/api/v1/market/detail` API 구현 및 성공/입력오류/제공자오류 경로의 모든 백엔드 테스트 통과.
3. **단계 3: 프론트엔드 스타일 및 탭 내비게이션 기반 조성**
   - 파일: `index.css`, `App.jsx`, `components/TabNavigation.jsx`
   - 완료 기준: 탭 네비게이션이 대시보드와 설정 탭을 정상 연동하며 세련된 premium dark 스타일이 적용됨.
4. **단계 4: 설정 탭 및 종목 추가/제거 구현**
   - 파일: `components/SettingsTab.jsx`
   - 완료 기준: 디바운스 검색이 작동하고 주식/ETF 검색 결과에서 추가 클릭 시 탭 추가 및 `localStorage` 반영, 중복 추가 시 기존 탭 이동, 설정에서 종목 제거 시 탭 삭제.
5. **단계 5: 종목 상세 및 SVG 인터랙티브 차트 구현**
   - 파일: `components/StockDetailTab.jsx`, `components/StockChart.jsx`
   - 완료 기준: 1D/1M/3M/1Y 기간 선택에 맞추어 시세 카드와 SVG 차트 라인/채우기가 고급스럽게 렌더링되며, 모바일 반응형 및 마우스 호버 툴팁 연동 완료.

## 위험 구간
- **위험 항목 1: Yahoo Finance API의 속도 저하 또는 무작위 차단 위험.**
  - 완화 방안: 기존 캐시 메커니즘을 검색 및 상세 API에도 적용하고 타임아웃을 적절히 설정하며 부분 실패 시 깨지지 않도록 결측 상태 처리.
- **위험 항목 2: SVG 자체 렌더링 차트의 모바일 화면 깨짐 또는 데이터 포인트가 없을 때의 오류.**
  - 완화 방안: SVG의 `viewBox`와 반응형 width를 적용하고 포인트가 없는 결측 상태에 대한 빈 화면/안내 배너 처리 추가.

## 새 의존성
- 없음

## 테스트 전략
- **백엔드 테스트 (`tests/` 하위)**:
  - MockAdapter를 통한 `/api/v1/market/search`의 1글자 미만/50글자 초과 400 에러, 허용되지 않은 유형 필터링 검증.
  - `/api/v1/market/detail`의 정상 200 응답 스키마 정합성 검증, Yahoo API 실패 시의 502/500 안전 예외 변환 검증.
- **프론트엔드 수동 검증**:
  - 탭 네비게이션 추가/제거 및 새로고침 후 `localStorage` 복구 검증.
  - SVG 차트 툴팁의 좌표 계산 및 마우스 이동 시 정상 표시 여부 검증.

## 롤백 / 복구 방향
- 변경 실패 시 `git reset --hard HEAD`를 통해 이전 커밋인 `da160df675d1918bbcb4b761ad53e043bacbff08`로 즉시 롤백 가능.

## 실행 승인
- risk_level: medium
- human_gate_required: true
- human_gate_reason: 검색/상세 API의 백엔드 연동과 탭 상태 및 SVG 차트라는 대형 프론트엔드 변경이 수반되어 안전성과 사용자 경험을 사람이 승인해야 함.
- approval_required_before_develop: true

## 스펙 모호점 처리
- **검색 API 호출 방지**: 과도한 API 호출 및 성능 저하 방지를 위해 글자 수가 1자 미만이거나 50자를 초과하는 경우 클라이언트와 서버에서 즉시 차단 처리함.

## Git 기준점
- base_commit: da160df675d1918bbcb4b761ad53e043bacbff08
- diff_base_command: git diff da160df675d1918bbcb4b761ad53e043bacbff08

## 사용자 확인 사항
- defaults_mode가 true이므로 추가 질문 없이 권장 기본값을 적용함.

## 단계 결과
- status: PASS
- next_stage: 02_develop
- human_gate_required: true
- blocking_reason: 없음
- risk_level: medium
- produced_files:
  - .ai/features/search/01_plan.md
- changed_files:
- commit_created: false
- commit_message:
- model_mismatch: false
- actual_model: Antigravity
