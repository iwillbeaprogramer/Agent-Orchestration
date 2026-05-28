# 03_review - project-initialize

작성: Antigravity
일시: 2026-05-28

## 리뷰 대상
- 검토한 파일 목록
  - `src/backend/main.py`
  - `src/backend/app/config.py`
  - `src/backend/app/adapters/base.py`
  - `src/backend/app/adapters/mock_adapter.py`
  - `src/backend/app/schemas/market.py`
  - `src/frontend/src/App.jsx`
  - `src/frontend/src/components/DashboardSection.jsx`
  - `src/frontend/src/components/MarketItemCard.jsx`
  - `src/frontend/src/components/StatusBanner.jsx`
  - `src/frontend/src/index.css`
  - `tests/backend/conftest.py`
  - `tests/backend/test_adapters.py`
  - `tests/backend/test_api.py`
  - `tests/backend/test_schemas.py`
- base_commit: `087a012aaf462c192297ca48fa4c656fdb9f968b`
- review_target_commit: `a453cf72dee482542a4b004760eea8383bfb2369`
- diff_command: `git diff 087a012aaf462c192297ca48fa4c656fdb9f968b..a453cf72dee482542a4b004760eea8383bfb2369`
- diff_range: `087a012aaf462c192297ca48fa4c656fdb9f968b..a453cf72dee482542a4b004760eea8383bfb2369`

## 지적 사항 요약
- BLOCKER: 0개
- MAJOR: 2개
- MINOR: 2개
- NIT: 2개

---

## 코드 품질

### 지적 사항 1
- severity: **MAJOR**
- 지적 사항: 등락률 `changePercent`가 0(보합)이거나 데이터 누락(`null/undefined`) 시 무조건 상승(`positive`) 테마로 오인 표시되는 문제
- 해당 코드 위치:
  - [src/frontend/src/components/MarketItemCard.jsx:L22-L23](file:///D:/test/vibe-coding-toolkit/Agent%20Orchestration/src/frontend/src/components/MarketItemCard.jsx#L22-L23)
  - [src/frontend/src/App.jsx:L12](file:///D:/test/vibe-coding-toolkit/Agent%20Orchestration/src/frontend/src/App.jsx#L12)
- 왜 문제인지:
  - `MarketItemCard.jsx`에서 `const changePercent = item.changePercent ?? 0;` 및 `const tone = changePercent >= 0 ? 'positive' : 'negative';` 로직을 사용하고 있습니다. 만약 등락률이 `null`이거나(데이터 정규화 실패, API 예외 등) 정확히 `0`일 때, 모두 상승(`positive`)으로 처리되어 화면의 카드 보더 및 상태선이 초록색으로 칠해집니다.
  - 이는 등락이 없는 보합 상태이거나 데이터에 오류가 생겼음에도 사용자에게 마치 상승세인 것처럼 오해를 불러일으킬 소지가 큽니다.
- 어떻게 개선해야 하는지:
  - `tone` 판별 로직을 중립(보합/오류) 상태를 고려하여 삼분할화합니다.
    ```javascript
    let tone = 'neutral';
    if (item.changePercent > 0) tone = 'positive';
    else if (item.changePercent < 0) tone = 'negative';
    ```
  - `App.jsx`의 요약 통계(`getSectionSummary`)에서도 단순히 `>= 0`으로 상승에 집계하지 말고, `changePercent > 0`, `changePercent < 0` 그리고 보합/기타 상태를 다루도록 집계 분기를 세분화하고, CSS(`index.css`)에 `.marketCard.neutral::before` 등 중립용 스타일링(예: 회색 또는 청회색 라인)을 보완해야 합니다.

### 지적 사항 2
- severity: **MINOR**
- 지적 사항: 백엔드 API 컨트롤러에서의 외부 어댑터 예외 방어 부재
- 해당 코드 위치:
  - [src/backend/main.py:L30-L33](file:///D:/test/vibe-coding-toolkit/Agent%20Orchestration/src/backend/main.py#L30-L33)
- 왜 문제인지:
  - `/api/v1/market/dashboard` 라우터 함수 내에서 `market_data_adapter.get_dashboard_data()`를 직접 호출하고 있습니다.
  - 현재는 동적 Mock 어댑터이지만 추후 실제 외부 시세 제공 API 등으로 어댑터를 교체했을 때, 네트워크 지연, API 키 만료, 데이터 형식 에러 등 다양한 예외 상황이 발생할 수 있습니다. 
  - 컨트롤러 레이어에서 `try-except` 블록으로 이를 방어하지 않으면 FastAPI는 내부 스택 트레이스와 함께 브라우저 및 사용자에게 날것의 500 Internal Server Error 응답을 보냅니다. 이는 보안성 및 운영 편의성을 저해합니다.
- 어떻게 개선해야 하는지:
  - `getMarketDashboard` 라우터 함수 내부에서 `try-except` 구문을 활용해 어댑터 예외를 잡아두고, 에러 로그를 남긴 후 `HTTPException(status_code=500, detail="...")` 형태의 사용자 친화적이고 안전한 가공 에러 응답을 제공하도록 아키텍처를 개선해야 합니다.

---

## 구조 및 가독성

### 지적 사항 1
- severity: **MINOR**
- 지적 사항: 등락가(`change`) 표시 시 양수(상승) 부호 `+` 표시 유실
- 해당 코드 위치:
  - [src/frontend/src/components/MarketItemCard.jsx:L40-L41](file:///D:/test/vibe-coding-toolkit/Agent%20Orchestration/src/frontend/src/components/MarketItemCard.jsx#L40-L41)
- 왜 문제인지:
  - 등락율(`changePercent`)은 `+0.67%`와 같이 플러스 기호가 명시적으로 잘 표시되지만, 등락가(`change`)는 단순히 `18.21`로 양의 부호 없이 표시되어 UI 상의 표현 일치성이 떨어집니다. 주식 대시보드에서는 통상 등락가와 등락율 모두 상승 시에 `+` 부호를 붙여 통일성을 유지합니다.
- 어떻게 개선해야 하는지:
  - `change` 변수도 등락율 포맷터처럼 양수일 때 앞선 기호(`+`)를 동반하여 표시할 수 있는 포맷 함수(예: `formatChangeValue`)를 생성하거나 적용하도록 가독성과 시각적 우수성을 개선합니다.

### 지적 사항 2
- severity: **NIT**
- 지적 사항: `MarketItemCard.jsx` 내 불필요한 삼항 연산자 조건문 잔재
- 해당 코드 위치:
  - [src/frontend/src/components/MarketItemCard.jsx:L7-L8](file:///D:/test/vibe-coding-toolkit/Agent%20Orchestration/src/frontend/src/components/MarketItemCard.jsx#L7-L8)
- 왜 문제인지:
  - `formatNumber` 포맷 함수 내에 `maximumFractionDigits: currency === 'KRW' ? 2 : 2` 라는 형태의 무의미한 삼항연산자가 작성되어 있습니다. 조건 결과가 모두 2로 동일하므로 불필요한 연산 코드입니다.
- 어떻게 개선해야 하는지:
  - 단순히 `maximumFractionDigits: 2` 로 정리하여 코드 가독성과 간결성을 확보합니다.

### 지적 사항 3
- severity: **NIT**
- 지적 사항: 백엔드 Python 파일 내 비 PEP 8(카멜케이스) 네이밍 관행 혼용
- 해당 코드 위치:
  - [src/backend/main.py:L26](file:///D:/test/vibe-coding-toolkit/Agent%20Orchestration/src/backend/main.py#L26), [src/backend/main.py:L31](file:///D:/test/vibe-coding-toolkit/Agent%20Orchestration/src/backend/main.py#L31)
  - [src/backend/app/schemas/market.py:L8](file:///D:/test/vibe-coding-toolkit/Agent%20Orchestration/src/backend/app/schemas/market.py#L8), [src/backend/app/schemas/market.py:L33](file:///D:/test/vibe-coding-toolkit/Agent%20Orchestration/src/backend/app/schemas/market.py#L33)
- 왜 문제인지:
  - Python 코드 내부 함수명과 파이썬 메서드명(`getHealth`, `getMarketDashboard`, `normalizeFiniteNumber`, `validateFiniteNumber`)이 PEP 8 스타일인 snake_case 대신 JavaScript/TypeScript 스타일인 camelCase로 설계되었습니다.
  - Project Contract 상 "명확한 네이밍 관례가 없으면 변수와 함수는 camelCase를 기본으로 한다"고 명시되어 있어 계약상으로 위반은 아니지만, 백엔드 파이썬 코드 컨벤션의 일관성 관점에서는 다소 이례적일 수 있어 권장 제안으로 남깁니다.
- 어떻게 개선해야 하는지:
  - 차후 프로젝트 통일 성격에 따라 프론트엔드는 camelCase, 백엔드는 snake_case로 이원화하는 방침을 세우거나, 현 상태를 유지한다면 주석을 통해 사유를 간략히 명시할 수 있습니다.

---

## 계획 대비 구현 일치성
- severity: **None (일치)**
- 01_plan.md 대비 일치/불일치 항목:
  - 의존성 구성: 100% 일치 (`fastapi`, `uvicorn`, `pydantic`, `react`, `react-dom`, `vite`)
  - 파일 구성 및 위치: 100% 일치 (`src/backend`, `src/frontend` 분리 및 보조 파일의 루트 배치 금지 준수)
  - 안정적 데이터 정규화: 100% 일치 (NaN/Infinity 정규화 Pydantic 유효성 검사기 탑재)
- 구체적 차이: 없습니다. 계획된 6단계 개발 일정에 명시된 아티팩트 파일과 아키텍처적 위험 완화 장치들이 매우 성실하게 완성되었습니다.
- 이 차이가 문제인지, 허용 가능한지: 차이가 전혀 없으므로 완벽히 허용 가능합니다.

---

## 구현 의도 타당성
- severity: **None (동의)**
- 02_dev.md에 적힌 판단에 대한 동의 또는 반론:
  - 자격 증명이 부재한 초기 단계를 위해 `MarketDataAdapter` 추상 인터페이스를 선언하고 하위에 변동 노이즈가 더해진 동적 `MockMarketDataAdapter`를 두어 데이터 바인딩을 완료한 아키텍처 설계 의도에 적극 동의합니다.
  - Vite의 프록시 설정을 `VITE_API_PROXY_TARGET` 환경변수로 덮어쓸 수 있도록 로컬 충돌 완화 장치를 제공한 부분 역시 타당합니다.
- 반론 시 근거: 반론 없음.

---

## 테스트

### 지적 사항 1
- severity: **MAJOR**
- 누락된 테스트 케이스: 백엔드 API 에러/예외 발생(실패 경로) 테스트 시나리오 누락
- 각 케이스가 왜 필요한지:
  - 현재 `test_api.py`와 `test_schemas.py` 등은 오직 성공 경로(200 OK, NaN/Infinity None 변환 성공)만을 위주로 작성되어 있습니다.
  - 외부 어댑터나 네트워크 등 비즈니스 로직 레벨에서 치명적인 예외가 일어났을 때, 서버가 다운타임 없이 안정적으로 핸들링하여 구조화된 JSON API 오류 응답을 내려보내는지 검증하는 "실패 시나리오 테스트"가 완전히 부재합니다.
  - 안정적이고 단단한 주식 대시보드를 유지하려면, 오류 주입 시의 처리 검증 테스트가 반드시 보완되어야 합니다.

---

## 04_fix 입력
- must_fix:
  - `MAJOR` 등락률 `changePercent` 0(보합) 및 `null` 상태 시 상승(`positive`) 테마 오지정 및 오집계 현상 UI 개선 (App.jsx, MarketItemCard.jsx, index.css)
  - `MAJOR` 백엔드 API의 실패 경로(예외 발생 상황) 검증 테스트 케이스 보완 (test_api.py)
- should_consider:
  - `MINOR` 백엔드 main.py 라우터에서 어댑터 예외 처리를 방어하는 try-except 컨트롤러 예외 안전 가이드 보완
  - `MINOR` `MarketItemCard.jsx`에서 등락가(`change`) 표시 시 양수일 때 플러스(`+`) 기호 보완
- optional:
  - `NIT` `MarketItemCard.jsx` 내의 무의미한 소수점 포맷 삼항연산자 (`currency === 'KRW' ? 2 : 2`) 제거
  - `NIT` Python 백엔드 명명 규칙을 가능한 PEP 8(snake_case)로 일원화할지 여부 결정 검토

---

## 총평
- 이번 `project-initialize` 단계의 전체적인 구현 품질은 매우 훌륭합니다. 프로젝트 루트에 의존성 및 보조 설정 파일을 절대 생성하지 않는다는 까다로운 '경로 원칙'을 `src/backend`와 `src/frontend` 폴더 분리로 완벽히 극복했습니다.
- 백엔드와 프론트엔드가 실질적으로 분리되어 동작하면서도 Pydantic을 활용하여 안전하게 NaN/Infinity 값을 `None`으로 정규화하는 신뢰성 정책을 계획대로 깔끔하게 준수했습니다.
- UI 디자인 토큰과 다크 테마 기반의 Glassmorphism CSS도 프리미엄급 품질을 선보이고 있습니다.
- 다만, 등락이 0(보합)이거나 데이터가 존재하지 않는 특수한 비정상 시나리오에서 화면에 무조건 초록색 상승 테마로 표시되어 발생하는 심각한 UI 오해 가능성(MAJOR) 및 API 예외/실패 경로에 대한 안전한 방어막과 그에 대응하는 테스트(MAJOR/MINOR)가 보완된다면 완결성을 지닌 완벽한 시스템이 될 것으로 사료됩니다.

---

## 단계 결과
- status: PASS
- next_stage: 04_fix
- human_gate_required: false
- blocking_reason: 없음
- risk_level: medium
- produced_files:
  - .ai/features/project-initialize/03_review.md
  - .ai/features/project-initialize/03_review.result.json
- changed_files:
  - .ai/features/project-initialize/03_review.md
  - .ai/features/project-initialize/03_review.result.json
- commit_created: false
- commit_message:
- model_mismatch: false
- actual_model: Antigravity
