# 01_plan - project-initialize

작성: Antigravity
일시: 2026-05-28

## 기능 목표
- React 화면과 FastAPI 백엔드를 사용해 주식/시장 대시보드 프로젝트의 초기 골격을 구축한다.
- 미국 대표지수, 한국 대표지수, 기타국 대표지수, 주요 환율을 구역별로 나누어 한 화면에 볼 수 있는 다크 테마 기반의 반응형 대시보드를 제공한다.

## 구현 접근 방식
- **역할 및 디렉토리 분리**: 프로덕션 코드를 루트 `src/` 하위에만 두어야 하는 프로젝트 계약을 준수하기 위해 백엔드는 `src/backend/`, 프론트엔드는 `src/frontend/` 디렉토리에 전적으로 배치한다. 빌드 및 설정 파일(`requirements.txt`, `package.json` 등)도 루트에 생성하지 않고 각각의 서브디렉토리에 포함한다.
- **어댑터 기반 데이터 제공**: 외부 시장 API 키나 자격 증명이 없는 초기 단계를 위해 `MarketDataAdapter` 추상 인터페이스를 설계하고, 실시간 변화와 같은 변동성 노이즈가 더해진 동적 목 데이터를 제공하는 `MockMarketDataAdapter`를 구현하여 연동한다.
- **안정적인 데이터 정규화**: Pydantic v2 모델의 유효성 검증(`field_validator` 등)을 통해 JSON 직렬화 전 NaN, Infinity와 같은 비표준 부동소수점 데이터를 `None`으로 정규화하여 프론트엔드에 `null`로 안전하게 내보낸다. 등락률 단위 또한 백분율 기준(%)으로 고정하여 중복 변환이나 단위 혼선을 방지한다.
- **미적 우수성(Aesthetics) 확보**: Vanilla CSS로 Sleek Dark 모드를 기본 채택하고, Glassmorphism 효과, Hover 시 미세한 스케일 애니메이션, 텍스트 상태 변경에 따른 마이크로 트랜지션, 상태별 Skeleton UI를 제공하여 매우 프리미엄한 사용자 인터페이스를 선사한다.

## 검토한 대안
- **대안 1: 단일 저장소 하이브리드 배치 (채택)**
  - 내용: `src/backend`와 `src/frontend`로 물리적 폴더를 나누고, 독립된 모듈로 의존성 및 코드를 관리하되 `src/` 루트 하위에 위치시킨다.
  - 장점: 백엔드와 프론트엔드의 역할이 엄격하게 분리되어 코드 유지보수성이 높고, 프로젝트 계약의 경로 원칙을 100% 준수한다.
  - 단점: 각각의 폴더 내부로 이동하여 패키지 설치 및 실행을 수행해야 한다.
  - 채택 이유: 프로젝트 계약에서 요구하는 '프로덕션 코드는 루트 `src/` 하위에 둔다'와 '보조 파일도 루트에 만들지 말고 반드시 `src/` 또는 `tests/` 하위에 둔다'는 하드 룰을 준수할 수 있는 유일한 설계이다.
- **대안 2: 루트에 설정 파일(package.json 등) 배치 및 단일 모노레포 빌드 구성 (기각)**
  - 내용: 루트 디렉토리에 `package.json`이나 `pyproject.toml`을 두어 패키지 설치를 한 곳에서 처리한다.
  - 장점: 개발 시 최상위 루트 디렉토리에서 한 번의 명령으로 모든 의존성을 빌드 및 실행할 수 있어 개발 생산성이 향상된다.
  - 단점: 프로젝트 계약의 경로 원칙("설정 파일, 의존성 파일, 실행 스크립트 같은 보조 파일도 루트에 만들지 않는다")을 명백히 위반한다.
  - 기각 사유: 계약 조건 위반으로 인한 기각.

## 변경 파일 계획
- **src/backend/requirements.txt (신규)**: FastAPI, Uvicorn, Pydantic v2 등 백엔드 구동에 필요한 라이브러리 목록 명시.
- **src/backend/main.py (신규)**: FastAPI 애플리케이션 생성, CORS 설정 적용 및 `/api/v1/market/dashboard` 집계 API 엔드포인트 라우팅 제공.
- **src/backend/app/__init__.py (신규)**: Python 패키지 마커.
- **src/backend/app/config.py (신규)**: CORS 도메인, 개발 모드 여부 등의 설정을 관리하는 설정 모듈.
- **src/backend/app/adapters/__init__.py (신규)**: Python 패키지 마커.
- **src/backend/app/adapters/base.py (신규)**: 시장 데이터 조회를 위한 `MarketDataAdapter` 추상 베이스 클래스 정의.
- **src/backend/app/adapters/mock_adapter.py (신규)**: 미국지수, 한국지수, 기타지수, 환율에 대해 노이즈(등락)가 적용된 동적 Mock 데이터를 생성하는 `MockMarketDataAdapter` 구현.
- **src/backend/app/schemas/__init__.py (신규)**: Python 패키지 마커.
- **src/backend/app/schemas/market.py (신규)**: 대시보드 API 응답 형식과 개별 종목 정보를 검증하고, NaN/Infinity 값을 `None`으로 정규화 처리하는 Pydantic 모델 설계.
- **src/frontend/package.json (신규)**: Vite, React, React DOM 등의 개발/운영 의존성 정의.
- **src/frontend/vite.config.js (신규)**: Vite 빌드 설정 및 백엔드 API 프록시(`/api` -> `http://localhost:8000`) 설정.
- **src/frontend/index.html (신규)**: 웹 애플리케이션 진입 HTML 파일 (Inter 폰트 링크 포함).
- **src/frontend/src/main.jsx (신규)**: React 엔트리 렌더링 파일.
- **src/frontend/src/index.css (신규)**: 프리미엄 다크 테마 CSS 변수, 레이아웃 그리드, Glassmorphism 스타일 및 미세 애니메이션 정의.
- **src/frontend/src/App.jsx (신규)**: 4개 섹션(미국 지수, 한국 지수, 기타국 지수, 환율)의 화면 렌더링, API fetch 로직, 새로고침 인터랙션 통합 구현.
- **src/frontend/src/components/DashboardSection.jsx (신규)**: 개별 시장 섹션을 카드 목록이나 테이블 형태로 그리는 컴포넌트.
- **src/frontend/src/components/MarketItemCard.jsx (신규)**: 종목명, 심볼, 현재가, 등락 정보, 리포팅 시각을 깔끔하게 그리는 카드 컴포넌트 (상승 시 녹색, 하락 시 적색 플로우 및 글래스모피즘 보더 처리).
- **src/frontend/src/components/StatusBanner.jsx (신규)**: 로딩 스켈레톤, 데이터 없음, API 실패 시의 재시도 버튼을 포함하는 상태 컴포넌트.
- **tests/backend/test_api.py (신규)**: FastAPI TestClient를 활용하여 집계 API의 정상 호출 및 스키마 유효성을 검증하는 통합 테스트.
- **tests/backend/test_adapters.py (신규)**: `MockMarketDataAdapter`가 4개 섹션의 적합한 주식 및 환율 데이터를 올바르게 생성하는지 검증하는 단위 테스트.
- **tests/backend/test_schemas.py (신규)**: NaN 또는 Infinity 값이 포함되었을 때 Pydantic 모델이 오류 없이 `None`으로 정상 정규화하는지 확인하는 단위 테스트.

## 데이터 / 제어 흐름
- 사용자가 프론트엔드 대시보드 진입 또는 `새로고침` 클릭 -> 프론트엔드가 `/api/v1/market/dashboard` 집계 API 호출.
- FastAPI가 요청 수신 -> `MockMarketDataAdapter` 인스턴스를 통해 원본 시장 데이터 조회.
- 어댑터가 임의의 변동폭을 반영한 시세 데이터를 생성하여 딕셔너리 형태로 반환.
- FastAPI가 반환받은 데이터를 `DashboardResponse` Pydantic 모델에 입력.
- Pydantic 모델 내의 validator가 각 수치 필드(value, change, changePercent)의 NaN/Infinity 여부를 판별하여 정규화 처리.
- 정규화된 데이터가 포함된 안전한 JSON 응답을 프론트엔드로 반환.
- 프론트엔드는 응답 데이터를 수신하여 4분할 그리드(Grid) 레이아웃에 매핑하고 렌더링.

```
+------------------+             +-----------------+             +--------------------------+
|  React Frontend  | --(fetch)--> | FastAPI Backend | --(query)--> |  MarketDataAdapter (ABC) |
|  (App.jsx Grid)  | <--(JSON)--- | (main.py Router)|               +--------------------------+
+------------------+              +--------+--------+                            |
        ^                                  |                                     v
        |                            (Normalizes NaN)               +--------------------------+
  Renders Sleek                     +------v-------+                |  MockMarketDataAdapter   |
  Dark Dashboard                    |   Pydantic   |                |    (Dynamic Sim Data)    |
                                    |    Schema    |                +--------------------------+
                                    +--------------+
```

## 구현 단계 분할
1. **단계 1: 백엔드 어댑터 설계 및 데이터 생성 구현**
   - 파일: `src/backend/app/adapters/base.py`, `src/backend/app/adapters/mock_adapter.py`
   - 완료 기준: 추상 클래스 구조가 설계되고, 목 어댑터가 등락 정보가 가미된 실시간 느낌의 지수/환율 데이터를 반환함.
2. **단계 2: 백엔드 Pydantic 스키마 설계 및 데이터 정규화 구현**
   - 파일: `src/backend/app/schemas/market.py`
   - 완료 기준: 수치 정규화(NaN/Infinity -> null) 로직이 삽입된 Pydantic 모델이 에러 없이 동작하고, 등락률의 백분율 단위 처리가 완료됨.
3. **단계 3: FastAPI 서버 초기화 및 집계 API 연동**
   - 파일: `src/backend/main.py`, `src/backend/requirements.txt`, `src/backend/app/config.py`
   - 완료 기준: FastAPI가 구동되고 `/api/v1/market/dashboard` API가 Pydantic 정규화된 데이터를 성공적으로 반환함.
4. **단계 4: 백엔드 통합 및 단위 테스트 작성 및 검증**
   - 파일: `tests/backend/test_api.py`, `tests/backend/test_adapters.py`, `tests/backend/test_schemas.py`
   - 완료 기준: `pytest` 실행 시 API 성공, 어댑터 데이터 무결성, NaN 정규화 테스트 케이스가 모두 PASS함.
5. **단계 5: 프론트엔드 React/Vite 환경 설정 및 디자인 토큰 구현**
   - 파일: `src/frontend/package.json`, `src/frontend/vite.config.js`, `src/frontend/index.html`, `src/frontend/src/index.css`
   - 완료 기준: Vite 개발 서버가 정상 기동되고 프리미엄 다크 테마 스타일시트(글로벌 변수 및 디자인 토큰)가 준비됨.
6. **단계 6: 대시보드 화면 및 컴포넌트 구현**
   - 파일: `src/frontend/src/App.jsx`, `src/frontend/src/components/*`
   - 완료 기준: 4개 섹션(미국, 한국, 기타국, 환율)이 다크모드 그리드상에 정상 출력되고, 로딩 스켈레톤, API 실패 시 재시도, 새로고침 기능이 모두 조화롭게 렌더링됨.

## 위험 구간
- **위험 항목**: 프로젝트 계약상 빌드 보조 파일(`package.json`, `requirements.txt`)을 프로젝트 루트에 만들 수 없으므로 개발자의 초기 개발 환경 구축 시의 직관성이 다소 떨어질 수 있음.
  - **완화 방안**: 최상위 README.md에 `src/backend` 및 `src/frontend` 디렉토리로 진입하여 패키지를 설치하고 실행하는 커맨드를 매우 친절하게 가이드로 명시함.
- **위험 항목**: 백엔드 API 응답에 파이썬 float 연산 등으로 NaN 혹은 Infinity가 섞여 나갈 경우 브라우저 JSON 파서가 에러를 발생시킬 수 있음.
  - **완화 방안**: Pydantic의 `@field_validator`를 활용하여 수치 변환 중 NaN이나 Infinity가 감지되면 강제로 `None`으로 대치함으로써 JSON 응답 상 `null`로 출력되도록 완전 보장함.

## 새 의존성
- **백엔드 (Python)**:
  - `fastapi`, `uvicorn`: API 서버 구축 및 서빙을 위해 필수.
  - `pydantic`: 데이터 검증 및 안전한 직렬화/정규화 처리를 위해 필수.
- **프론트엔드 (Node.js)**:
  - `react`, `react-dom`: 대시보드 컴포넌트 렌더링을 위해 필수.
  - `vite`: 초고속 개발 및 번들링 빌드 환경을 구성하기 위해 필수.

## 테스트 전략
- **FastAPI API 통합 검증**: `tests/backend/test_api.py`에서 TestClient를 이용해 집계 API 응답 규격을 통째로 검증 (Integration).
- **데이터 공급 무결성 검증**: `tests/backend/test_adapters.py`에서 `MockMarketDataAdapter`가 4개 섹션(US, KR, Global, FX)의 정의된 항목을 누락 없이 반환하는지 검증 (Unit).
- **NaN 정규화 검증**: `tests/backend/test_schemas.py`에서 Pydantic 모델에 의도적으로 `float('nan')` 및 `float('inf')`를 주입했을 때, 직렬화 시 `None`으로 정교하게 필터링되는지 검증 (Unit).
- **브라우저 렌더링 및 인터랙션**: 브라우저 검사를 통한 UI 시각적 정합성 및 새로고침 작동 여부 수동 확인 (e2e 대체).

## 롤백 / 복구 방향
- 본 단계는 신규 구성(project-initialize)이므로 기존 코드를 훼손하지 않음.
- 코드 작성 단계에서 빌드 실패 혹은 요구사항 이탈 발생 시, 생성된 `src/` 및 `tests/` 하위의 신규 파일을 삭제하거나 `git checkout`을 통해 안전하게 초기 상태로 롤백할 수 있음.

## 실행 승인
- risk_level: high
- human_gate_required: true
- human_gate_reason: 초기 React 및 FastAPI 아키텍처 수립과 파일 레이아웃 배치, 어댑터 설계 및 미적 화면 UI 디자인 원칙이 정립되므로, 본격적인 코드 개발(02_develop) 단계 진입 전에 사람 승인이 필요하다.
- approval_required_before_develop: true

## 스펙 모호점 처리
- **환율 표기 관례**: 스펙 22번 라인의 "JPY/KRW 100엔 기준 표기 및 단위 명시" 요구사항에 따라, 어댑터 and 프론트엔드 라벨 표기 시 `JPY/KRW (100엔)`으로 단위를 명확히 표기하고 원본 수치는 백엔드에서 100엔 기준으로 스케일링하여 내려주도록 계획함.

## Git 기준점
- base_commit: 087a012aaf462c192297ca48fa4c656fdb9f968b
- diff_base_command: git diff 087a012aaf462c192297ca48fa4c656fdb9f968b

## 사용자 확인 사항
- 질문과 사용자 답변 기록: `defaults_mode: true` 정책에 따라 추가 질문 없이 스펙의 요구사항과 권장 기본값을 기준으로 설계를 PASS 확정함.

## 단계 결과
- status: PASS
- next_stage: 02_develop
- human_gate_required: true
- blocking_reason: 없음
- risk_level: high
- produced_files:
  - .ai/features/project-initialize/01_plan.md
- changed_files:
  - .ai/features/project-initialize/01_plan.md
- commit_created: false
- commit_message:
- model_mismatch: false
- actual_model: Antigravity
