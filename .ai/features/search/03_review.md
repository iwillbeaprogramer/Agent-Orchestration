# 03_review - search

작성: Gemini 3.5 Flash (High)
일시: 2026-05-29

## 리뷰 대상
- 검토한 파일 목록:
  - `src/backend/app/schemas/market.py`
  - `src/backend/app/adapters/base.py`
  - `src/backend/app/adapters/yahoo_adapter.py`
  - `src/backend/app/adapters/mock_adapter.py`
  - `src/backend/main.py`
  - `src/frontend/src/App.jsx`
  - `src/frontend/src/components/TabNavigation.jsx`
  - `src/frontend/src/components/SettingsTab.jsx`
  - `src/frontend/src/components/StockDetailTab.jsx`
  - `src/frontend/src/components/StockChart.jsx`
  - `src/frontend/src/index.css`
  - `tests/backend/test_adapters.py`
  - `tests/backend/test_api.py`
- base_commit: da160df675d1918bbcb4b761ad53e043bacbff08
- review_target_commit: 68a86c7f146ade5d2989b477cfd39f452eb1cf47
- diff_command: git diff da160df675d1918bbcb4b761ad53e043bacbff08..68a86c7f146ade5d2989b477cfd39f452eb1cf47
- diff_range: da160df675d1918bbcb4b761ad53e043bacbff08..68a86c7f146ade5d2989b477cfd39f452eb1cf47

## 지적 사항 요약
- BLOCKER: 0개
- MAJOR: 0개
- MINOR: 1개
- NIT: 2개

## 코드 품질
### 1. `_lookup_cache` 메모리 누적 가능성
- **severity**: MINOR
- **지적 사항**: `YahooMarketDataAdapter` 내의 상세 시세 및 검색 캐시(`_lookup_cache`)가 무제한 누적될 수 있습니다.
- **해당 코드 위치**: [yahoo_adapter.py:L105](file:///D:/test/vibe-coding-toolkit/Agent%20Orchestration/src/backend/app/adapters/yahoo_adapter.py#L105), [L198-L209](file:///D:/test/vibe-coding-toolkit/Agent%20Orchestration/src/backend/app/adapters/yahoo_adapter.py#L198-L209)
- **왜 문제인지**: 현재 구현된 `_get_lookup_cache`는 특정 key를 조회하는 시점에 만료 시간이 지났을 때만 캐시를 삭제(pop)합니다. 따라서 사용자가 조회하지 않는 무수히 많은 검색이나 상세 데이터 캐시가 메모리에 반영구적으로 잔존할 수 있어 메모리 사용량이 점진적으로 늘어날 위험이 있습니다.
- **어떻게 개선해야 하는지**: 캐시 항목 수 제한(LRU 패턴)을 도입하거나, 백그라운드 태스크 또는 캐시 삽입 시점에 주기적으로 만료된 캐시 키들을 정적 청소(cleanup)하는 로직을 추가하는 것이 좋습니다.

### 2. 수치 포맷팅 시 통화 기호 및 통화별 포맷팅 아쉬움
- **severity**: NIT
- **지적 사항**: 국내외 주식이 섞여 있으나 통화 포맷팅이 `ko-KR`로 일원화되어 있습니다.
- **해당 코드 위치**: [StockDetailTab.jsx:L15](file:///D:/test/vibe-coding-toolkit/Agent%20Orchestration/src/frontend/src/components/StockDetailTab.jsx#L15), [StockChart.jsx:L15](file:///D:/test/vibe-coding-toolkit/Agent%20Orchestration/src/frontend/src/components/StockChart.jsx#L15)
- **왜 문제인지**: 현재 미국 달러(USD) 주식도 한글 숫자 포맷터(`ko-KR`)를 사용해 `101.5`와 같이 표시되고 있습니다. 기능적인 버그는 아니나, `USD`나 `KRW` 등 통화 유형에 맞게 통화 기호(`$`, `₩`)나 통화별 특화된 포맷팅이 가미되면 사용자 경험(UX) 측면에서 한층 더 세련될 것입니다.
- **어떻게 개선해야 하는지**: `Intl.NumberFormat`에 통화 정보(`currency`)를 전달하여 옵션으로 스타일을 설정하거나, 컴포넌트 프롭으로 전달된 통화에 따른 포맷터를 유연하게 분기시키는 편이 완성도를 한층 높일 것입니다.

### 3. 거래소 상수 하드코딩 분리 권장
- **severity**: NIT
- **지적 사항**: 한국/미국 필터링을 위한 거래소 정보가 어댑터 클래스 본체에 하드코딩되어 있습니다.
- **해당 코드 위치**: [yahoo_adapter.py:L37-L38](file:///D:/test/vibe-coding-toolkit/Agent%20Orchestration/src/backend/app/adapters/yahoo_adapter.py#L37-L38)
- **왜 문제인지**: 현재 `US_EXCHANGES`와 `KR_EXCHANGES` 상수가 어댑터 내부에 내장되어 있어 설정 제어나 확장성이 제한됩니다.
- **어떻게 개선해야 하는지**: 추후 다국어 또는 타 국가 주식 확장성을 고려한다면, 해당 상수를 `app/config.py` 또는 공통 상수 정의용 모듈로 이동하는 편이 장기 유지보수 및 테스트 격리 면에서 유리합니다.

## 구조 및 가독성
- **severity**: NIT (지적 사항 없음)
- **지적 사항**: 전체 컴포넌트 및 백엔드 라우터 구조가 매우 견고하며 가독성이 우수합니다.
- **해당 코드 위치**: -
- **왜 문제인지**: -
- **어떻게 개선해야 하는지**: -

## 계획 대비 구현 일치성
- **severity**: NIT (완전 일치)
- **01_plan.md 대비 일치/불일치 항목**: 완전 일치
- **구체적 차이**: 없음
- **이 차이가 문제인지, 허용 가능한지**: `01_plan.md`에서 정의한 5개 마일스톤 및 새 스키마, 어댑터 명세, 프론트엔드 컴포넌트 추가 계획이 한 치의 오차도 없이 철저히 구현되었습니다. 새 외부 라이브러리 추가 없이 SVG 자체 렌더링으로 인터랙티브 차트를 구현한 결정은 `Project Contract`의 "최소 의존성 원칙"을 모범적으로 충실히 준수했습니다.

## 구현 의도 타당성
- **severity**: NIT (전적으로 동의)
- **02_dev.md에 적힌 판단에 대한 동의 또는 반론**: 전적으로 동의함.
- **반론 시 근거**: 02_dev에서 주식/ETF 검색 및 상세 기능을 기존 Pydantic/FastAPI 구조 내에서 매끄럽게 확장했고, 차트 라이브러리를 배제하고 순수 SVG 컴포넌트로 반응형 툴팁 차트를 만든 디자인 결정은 성능과 리소스 최적화 및 유지보수 편의를 동시에 잡은 훌륭한 선택이었습니다.

## 테스트
- **severity**: NIT (완벽함)
- **누락된 테스트 케이스**: 없음.
- **각 케이스가 왜 필요한지**: 20개의 백엔드 단위/통합 테스트가 작성되어 비정상 입력(길이 제한, 비지원 타입 필터링), 제공자 장애(502 에러 변환), 데이터 무결성 검증을 철저하게 해내고 있습니다. 또한 `npm run build`를 통한 Vite 프론트엔드 정적 빌드 검증 역시 완벽하게 성공했습니다.

## 04_fix 입력
- **must_fix**:
  - 없음 (BLOCKER 및 MAJOR 등급의 중대 버그나 스펙 누락은 전혀 발견되지 않음)
- **should_consider**:
  - `_lookup_cache` 메모리 누수 완화 대책 (Eviction/Cleanup 정책 도입 고려)
- **optional**:
  - 통화 포맷팅 고도화 (USD/KRW에 맞춘 통화 표시 및 기호 렌더링)
  - 거래소 상수의 `app/config.py` 이관

## 총평
2단계 개발을 통해 구현된 "주식/ETF 검색 및 개별 탭 추가 기능"은 스펙 및 설계 계획과 완전히 부합하며, 구현 수준이 대단히 고도화되어 있습니다. 
특히 경쟁 상태를 완벽히 해결하기 위한 `AbortController` 사용, 수치 결측 데이터 및 NaN/Infinity에 대한 이중 정규화 검증, 시각적으로 수려한 Premium Dark 테마 CSS 스타일 및 반응형 자체 SVG 차트 드로잉은 프로덕션급 웹 애플리케이션에 걸맞은 극상의 품질을 갖추고 있습니다. 심각한 오류나 스펙 누락이 존재하지 않으므로 본 단계는 기쁘게 **PASS** 처리합니다.

## 단계 결과
- status: PASS
- next_stage: 04_fix
- human_gate_required: false
- blocking_reason: 없음
- risk_level: low
- produced_files:
  - .ai/features/search/03_review.md
- changed_files:
- commit_created: false
- commit_message:
- model_mismatch: false
- actual_model: Gemini 3.5 Flash (High)
