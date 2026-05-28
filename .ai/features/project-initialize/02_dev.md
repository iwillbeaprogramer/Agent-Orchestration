# 02_dev - project-initialize

작성: Codex
일시: 2026-05-28

## 기능 목표
- React 화면과 FastAPI 백엔드로 주식/시장 대시보드 초기 프로젝트를 구성했다.
- 첫 화면에서 미국 대표지수, 한국 대표지수, 기타국 대표지수, 주요 환율을 구역별로 조회하고 새로고침할 수 있게 했다.

## 변경 파일
- .ai/features/project-initialize/00_spec.md (입력 / 변경 금지)
- .ai/features/project-initialize/01_plan.md (입력 / 변경 금지)
- .ai/features/project-initialize/02_dev.md (신규)
- .ai/features/project-initialize/02_dev.result.json (신규)
- src/backend/requirements.txt (신규)
- src/backend/main.py (신규)
- src/backend/app/__init__.py (신규)
- src/backend/app/config.py (신규)
- src/backend/app/adapters/__init__.py (신규)
- src/backend/app/adapters/base.py (신규)
- src/backend/app/adapters/mock_adapter.py (신규)
- src/backend/app/schemas/__init__.py (신규)
- src/backend/app/schemas/market.py (신규)
- src/frontend/package.json (신규)
- src/frontend/package-lock.json (신규)
- src/frontend/vite.config.js (신규)
- src/frontend/index.html (신규)
- src/frontend/src/main.jsx (신규)
- src/frontend/src/App.jsx (신규)
- src/frontend/src/index.css (신규)
- src/frontend/src/components/DashboardSection.jsx (신규)
- src/frontend/src/components/MarketItemCard.jsx (신규)
- src/frontend/src/components/StatusBanner.jsx (신규)
- tests/backend/conftest.py (신규)
- tests/backend/test_adapters.py (신규)
- tests/backend/test_api.py (신규)
- tests/backend/test_schemas.py (신규)

## 구현 내용
- FastAPI 앱에 `/api/v1/health`, `/api/v1/market/dashboard` 엔드포인트를 추가했다.
- `MarketDataAdapter` 추상 인터페이스와 `MockMarketDataAdapter`를 분리해 외부 데이터 제공자 교체 지점을 만들었다.
- Pydantic v2 스키마에서 `value`, `change`, `changePercent`의 NaN/Infinity 값을 `None`으로 정규화해 JSON 응답에서 `null`로 나가게 했다.
- React/Vite 화면은 4개 섹션 그리드, 요약 스트립, 새로고침 버튼, 로딩 스켈레톤, 오류/빈 데이터 배너로 구성했다.
- Vite 프록시는 기본 `http://127.0.0.1:8000`을 사용하되, 로컬 포트 충돌에 대비해 `VITE_API_PROXY_TARGET` 환경변수로 override할 수 있게 했다.
- JPY/KRW 환율은 계획의 기본 결정대로 `JPY/KRW (100엔)`으로 단위를 명시했다.

## 왜 이렇게 구현했는가
- 실제 API 인증 정보가 없으므로 계획대로 mock adapter를 기본 구현으로 두고, 백엔드 비즈니스/API 레이어와 데이터 공급자를 분리했다.
- 루트에 설정 파일을 만들지 말라는 경로 원칙에 따라 백엔드 의존성은 `src/backend/requirements.txt`, 프론트 의존성은 `src/frontend/package.json`에만 배치했다.
- `pydantic-settings` 같은 계획 외 의존성은 추가하지 않고, CORS 설정은 단순 dataclass로 처리했다.
- `package-lock.json`은 프론트 의존성 재현성을 위해 `src/frontend` 하위에 함께 남겼다.
- 초기 Vite 5 계열 설치 후 `npm audit`에서 중간 등급 취약점이 보고되어, 현재 Node 24 환경과 호환되는 Vite 8 / plugin-react 6 계열로 올렸다.
- 기본 포트 `8000`, `5173`이 다른 로컬 프로세스에서 사용 중이어서 기존 프로세스를 종료하지 않고 대체 포트 검증을 수행했다.

## 새로 추가한 의존성
- fastapi: 백엔드 API 서버 구현.
- uvicorn: FastAPI 로컬 실행 서버.
- pydantic: API 응답 스키마 검증과 수치 정규화.
- react, react-dom: 프론트엔드 화면 구현.
- vite, @vitejs/plugin-react: React 개발 서버와 빌드 구성.

## 테스트
- 작성한 테스트 파일:
  - tests/backend/conftest.py
  - tests/backend/test_adapters.py
  - tests/backend/test_api.py
  - tests/backend/test_schemas.py
- 커버 범위:
  - mock adapter가 4개 섹션과 필수 시장 항목을 반환하는지 검증.
  - FastAPI 대시보드/헬스 엔드포인트 응답 검증.
  - NaN/Infinity 수치가 `None`으로 정규화되는지 검증.
- 실행한 테스트 명령:
  - `python -m pytest tests/backend`
  - `npm install`
  - `npm run build`
  - `npm audit --audit-level=moderate`
  - `Invoke-WebRequest http://127.0.0.1:5174/api/v1/market/dashboard`
- 테스트 실행 결과:
  - `python -m pytest tests/backend`: 6 passed
  - `npm run build`: PASS
  - `npm audit --audit-level=moderate`: found 0 vulnerabilities
  - 프론트 개발 서버 프록시 경유 API 호출: HTTP 200
- 브라우저 시각 검증:
  - Browser 플러그인 연결을 시도했으나 사용 가능한 브라우저 목록이 비어 있어 인앱 브라우저 렌더 검증은 수행하지 못했다.
  - 대신 Vite production build와 로컬 프론트 프록시 API 호출로 기능 연결을 확인했다.

## 알려진 한계 / 추후 개선 사항
- 현재 시장 데이터는 실제 시세가 아니라 mock 데이터다. 실제 공급자 연동 시 adapter 구현만 교체하면 된다.
- 차트, 사용자별 관심 종목, 알림, 인증은 이번 범위에서 제외했다.
- 인앱 브라우저가 세션에 연결되지 않아 스크린샷 기반 시각 검증은 다음 검증 단계에서 보완할 수 있다.
- 로컬 기본 포트 `8000`, `5173`은 현재 머신에서 이미 사용 중이었다. 이번 검증은 백엔드 `8010`, 프론트 `5174`로 수행했다.

## Git 정보
- base_commit: 087a012aaf462c192297ca48fa4c656fdb9f968b
- harness_commit_required: true
- commit_created_by_model: false
- commit_message_suggestion: project-initialize[20260528-154441][02_develop]
- commit_scope:
  - .ai/features/project-initialize/00_spec.md
  - .ai/features/project-initialize/00_spec.result.json
  - .ai/features/project-initialize/01_plan.md
  - .ai/features/project-initialize/01_plan.result.json
  - .ai/features/project-initialize/02_dev.md
  - .ai/features/project-initialize/02_dev.result.json
  - src/backend/
  - src/frontend/
  - tests/backend/
- pre_commit_diff_command: git diff 087a012aaf462c192297ca48fa4c656fdb9f968b
- changed_files:
  - .ai/features/project-initialize/02_dev.md
  - .ai/features/project-initialize/02_dev.result.json
  - src/backend/requirements.txt
  - src/backend/main.py
  - src/backend/app/__init__.py
  - src/backend/app/config.py
  - src/backend/app/adapters/__init__.py
  - src/backend/app/adapters/base.py
  - src/backend/app/adapters/mock_adapter.py
  - src/backend/app/schemas/__init__.py
  - src/backend/app/schemas/market.py
  - src/frontend/package.json
  - src/frontend/package-lock.json
  - src/frontend/vite.config.js
  - src/frontend/index.html
  - src/frontend/src/main.jsx
  - src/frontend/src/App.jsx
  - src/frontend/src/index.css
  - src/frontend/src/components/DashboardSection.jsx
  - src/frontend/src/components/MarketItemCard.jsx
  - src/frontend/src/components/StatusBanner.jsx
  - tests/backend/conftest.py
  - tests/backend/test_adapters.py
  - tests/backend/test_api.py
  - tests/backend/test_schemas.py
- harness_commit_blocking_reason: 없음

## 단계 결과
- status: PASS
- next_stage: 03_review
- human_gate_required: false
- blocking_reason: 없음
- risk_level: high
- produced_files:
  - .ai/features/project-initialize/02_dev.md
  - .ai/features/project-initialize/02_dev.result.json
- changed_files:
  - .ai/features/project-initialize/02_dev.md
  - .ai/features/project-initialize/02_dev.result.json
  - src/backend/requirements.txt
  - src/backend/main.py
  - src/backend/app/__init__.py
  - src/backend/app/config.py
  - src/backend/app/adapters/__init__.py
  - src/backend/app/adapters/base.py
  - src/backend/app/adapters/mock_adapter.py
  - src/backend/app/schemas/__init__.py
  - src/backend/app/schemas/market.py
  - src/frontend/package.json
  - src/frontend/package-lock.json
  - src/frontend/vite.config.js
  - src/frontend/index.html
  - src/frontend/src/main.jsx
  - src/frontend/src/App.jsx
  - src/frontend/src/index.css
  - src/frontend/src/components/DashboardSection.jsx
  - src/frontend/src/components/MarketItemCard.jsx
  - src/frontend/src/components/StatusBanner.jsx
  - tests/backend/conftest.py
  - tests/backend/test_adapters.py
  - tests/backend/test_api.py
  - tests/backend/test_schemas.py
- harness_commit_required: true
- commit_created_by_model: false
- commit_message_suggestion: project-initialize[20260528-154441][02_develop]
- test_commands:
  - python -m pytest tests/backend
  - npm install
  - npm run build
  - npm audit --audit-level=moderate
  - Invoke-WebRequest http://127.0.0.1:5174/api/v1/market/dashboard
- model_mismatch: true
- actual_model: Codex
