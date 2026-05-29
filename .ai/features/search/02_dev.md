# 02_dev - search

작성: Codex
일시: 2026-05-28

## 기능 목표
- 기존 대시보드를 첫 번째 메인 탭으로 유지하고, 사용자가 설정 탭에서 한국/미국 주식 및 ETF를 검색해 개별 종목 탭으로 추가할 수 있게 구현했다.
- 개별 종목 탭에서는 주요 시세 지표와 1D/1M/3M/1Y SVG 가격 차트를 제공한다.

## 변경 파일
- .ai/features/search/00_spec.md (입력 / 변경 금지)
- .ai/features/search/01_plan.md (입력 / 변경 금지)
- .ai/features/search/02_dev.md (신규)
- .ai/features/search/02_dev.result.json (신규)
- src/backend/app/schemas/market.py (수정)
- src/backend/app/adapters/base.py (수정)
- src/backend/app/adapters/yahoo_adapter.py (수정)
- src/backend/app/adapters/mock_adapter.py (수정)
- src/backend/main.py (수정)
- src/frontend/src/App.jsx (수정)
- src/frontend/src/components/DashboardSection.jsx (수정)
- src/frontend/src/components/StatusBanner.jsx (수정)
- src/frontend/src/components/SettingsTab.jsx (신규)
- src/frontend/src/components/StockChart.jsx (신규)
- src/frontend/src/components/StockDetailTab.jsx (신규)
- src/frontend/src/components/TabNavigation.jsx (신규)
- src/frontend/src/index.css (수정)
- tests/backend/test_adapters.py (수정)
- tests/backend/test_api.py (수정)

## 구현 내용
- 백엔드에 `/api/v1/market/search`, `/api/v1/market/detail` API를 추가하고, Yahoo Finance search/chart 응답을 주식/ETF 전용 응답 스키마로 정규화했다.
- Yahoo 검색 결과는 한국/미국 거래소의 주식과 ETF만 통과시키고, 상세 API도 주식/ETF가 아닌 응답은 거부하도록 처리했다.
- 상세 차트 응답은 `1D`, `1M`, `3M`, `1Y` 범위를 지원하며, NaN/Infinity 등 비유한 수치는 기존 스키마 패턴에 맞춰 `null`로 정규화한다.
- 프론트엔드는 `Dashboard -> 추가 종목 탭들 -> Settings` 순서의 탭 네비게이션을 만들고, 추가 종목은 `localStorage`에 저장한다.
- 설정 탭에는 디바운스 검색, 결과 추가, 중복 추가 시 기존 탭 열기, 저장된 종목 제거 기능을 구현했다.
- 종목 상세 탭에는 주요 가격/거래량/상태 지표와 자체 SVG 라인 차트를 구현했다.

## 왜 이렇게 구현했는가
- 01_plan의 방향대로 새 의존성을 추가하지 않고 기존 FastAPI, Pydantic, React 구조 안에서 구현했다.
- 외부 제공자 호출은 기존 `MarketDataAdapter` 추상화 뒤에 `search_symbols`, `get_stock_detail` 메서드를 추가해 비즈니스/API 경계와 분리했다.
- 차트는 Chart.js/Recharts를 도입하지 않고 SVG로 직접 렌더링해 계획의 의존성 제한을 지켰다.
- 브라우저 저장소는 현재 프로젝트에 계정/서버 저장소가 없으므로 기본 결정대로 `localStorage`를 사용했다.
- 기존 일부 UI 문자열이 깨져 빌드와 표시 안정성을 해칠 수 있어, 수정 대상 컴포넌트의 표시 문구는 ASCII 영문으로 정리했다.

## 새로 추가한 의존성
- 없음

## 테스트
- 작성/수정한 테스트 파일:
  - tests/backend/test_adapters.py
  - tests/backend/test_api.py
- 커버 범위:
  - Yahoo 검색 결과의 주식/ETF 및 한국/미국 필터링
  - Yahoo 상세 quote/chart 매핑
  - 상세 API의 비지원 상품 유형 거부
  - 검색/상세 API의 성공 경로와 입력 오류 경로
- 실행한 테스트 명령:
  - `python -m pytest tests -q`
  - `npm run build` (`src/frontend`)
  - 로컬 스모크: `GET /api/v1/health`, 프론트 HTML 200, `GET /api/v1/market/search?query=QLD`, `GET /api/v1/market/detail?symbol=QLD&range=1M`
- 테스트 실행 결과:
  - `22 passed in 0.61s`
  - Vite production build 성공
  - QLD 검색 및 1개월 상세 차트 응답 확인
- 의도적으로 테스트하지 않은 부분:
  - 프론트엔드 컴포넌트 단위 테스트는 현재 프로젝트에 테스트 러너가 없어 추가하지 않았다. 대신 Vite 빌드와 로컬 HTTP 스모크로 문법/번들/기본 응답을 확인했다.

## 알려진 한계 / 추후 개선 사항
- Yahoo Finance 비공식 엔드포인트를 사용하므로 제공자 응답 형식 변경이나 제한에 영향을 받을 수 있다.
- 검색/상세 데이터는 서버 메모리 TTL 캐시만 사용하므로 프로세스 재시작 시 캐시가 사라진다.
- 인앱 브라우저가 이 세션에서 사용 가능한 브라우저를 노출하지 않아 화면 캡처 기반 검증은 수행하지 못했다.
- 추후 프론트 테스트 환경이 생기면 탭 순서, `localStorage` 복구, 종목 추가/삭제 플로우를 자동화하는 테스트를 추가하는 것이 좋다.

## Git 정보
- base_commit: da160df675d1918bbcb4b761ad53e043bacbff08
- harness_commit_required: true
- commit_created_by_model: false
- commit_message_suggestion: search[20260528-164539][02_develop]
- commit_scope:
  - .ai/features/search/00_spec.md
  - .ai/features/search/00_spec.result.json
  - .ai/features/search/01_plan.md
  - .ai/features/search/01_plan.result.json
  - .ai/features/search/02_dev.md
  - .ai/features/search/02_dev.result.json
  - src/backend/app/schemas/market.py
  - src/backend/app/adapters/base.py
  - src/backend/app/adapters/yahoo_adapter.py
  - src/backend/app/adapters/mock_adapter.py
  - src/backend/main.py
  - src/frontend/src/App.jsx
  - src/frontend/src/components/DashboardSection.jsx
  - src/frontend/src/components/StatusBanner.jsx
  - src/frontend/src/components/SettingsTab.jsx
  - src/frontend/src/components/StockChart.jsx
  - src/frontend/src/components/StockDetailTab.jsx
  - src/frontend/src/components/TabNavigation.jsx
  - src/frontend/src/index.css
  - tests/backend/test_adapters.py
  - tests/backend/test_api.py
- pre_commit_diff_command: git diff da160df675d1918bbcb4b761ad53e043bacbff08
- changed_files:
  - .ai/features/search/02_dev.md
  - .ai/features/search/02_dev.result.json
  - src/backend/app/adapters/base.py
  - src/backend/app/adapters/mock_adapter.py
  - src/backend/app/adapters/yahoo_adapter.py
  - src/backend/app/schemas/market.py
  - src/backend/main.py
  - src/frontend/src/App.jsx
  - src/frontend/src/components/DashboardSection.jsx
  - src/frontend/src/components/SettingsTab.jsx
  - src/frontend/src/components/StatusBanner.jsx
  - src/frontend/src/components/StockChart.jsx
  - src/frontend/src/components/StockDetailTab.jsx
  - src/frontend/src/components/TabNavigation.jsx
  - src/frontend/src/index.css
  - tests/backend/test_adapters.py
  - tests/backend/test_api.py
- harness_commit_blocking_reason:

## 단계 결과
- status: PASS
- next_stage: 03_review
- human_gate_required: false
- blocking_reason: 없음
- risk_level: medium
- produced_files:
  - .ai/features/search/02_dev.md
  - .ai/features/search/02_dev.result.json
- changed_files:
  - src/backend/app/adapters/base.py
  - src/backend/app/adapters/mock_adapter.py
  - src/backend/app/adapters/yahoo_adapter.py
  - src/backend/app/schemas/market.py
  - src/backend/main.py
  - src/frontend/src/App.jsx
  - src/frontend/src/components/DashboardSection.jsx
  - src/frontend/src/components/SettingsTab.jsx
  - src/frontend/src/components/StatusBanner.jsx
  - src/frontend/src/components/StockChart.jsx
  - src/frontend/src/components/StockDetailTab.jsx
  - src/frontend/src/components/TabNavigation.jsx
  - src/frontend/src/index.css
  - tests/backend/test_adapters.py
  - tests/backend/test_api.py
- harness_commit_required: true
- commit_created_by_model: false
- commit_message_suggestion: search[20260528-164539][02_develop]
- test_commands:
  - python -m pytest tests -q
  - npm run build
- model_mismatch: true
- actual_model: Codex
