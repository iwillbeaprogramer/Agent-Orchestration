# 01_plan - debug

작성: Antigravity
일시: 2026-05-28

## 기능 목표
- 대시보드가 고정된 Mock 데이터 대신 실행 시점(2026-05-28 기준)을 반영하는 야후 파이낸스(Yahoo Finance) API의 실시간 데이터를 반환하도록 구현한다.
- 데이터 조회 지연을 방지하기 위한 캐싱 및 병렬화(ThreadPoolExecutor)를 적용하고, 네트워크 장애 및 부분 누락 시에도 안전한 응답 구조를 제공한다.

## 구현 접근 방식
- **신규 어댑터 (`YahooMarketDataAdapter`) 도입**:
  - `src/backend/app/adapters/yahoo_adapter.py`를 신규 작성하고, 기존 `MockMarketDataAdapter`와 동일한 `MarketDataAdapter` 추상 인터페이스를 상속받는다.
  - 야후 파이낸스 v8 Chart API (`https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d`)를 활용하여 각 지수와 환율에 대한 실시간 수치를 가져온다.
  - API 호출 시 `User-Agent` 헤더(`Mozilla/5.0 (Windows NT 10.0; Win64; x64)...`)를 설정하여 야후의 `401 Unauthorized` 차단 정책을 안정적으로 회피한다.
- **성능 및 안정성 강화**:
  - **병렬 쿼리 수행**: `concurrent.futures.ThreadPoolExecutor`를 사용하여 18개의 개별 시장 지수 및 환율을 동시에 병렬로 조회함으로써 API 응답 대기 시간을 최대 1초 내외로 대폭 단축한다.
  - **간이 메모리 캐시 (Short-term Cache)**: Yahoo API의 잦은 호출로 인한 차단(Rate Limiting) 방지와 응답 속도 최적화를 위해 60초 TTL(Time-To-Live)을 가지는 초간단 메모리 캐싱 로직을 어댑터 내부에 내장한다.
- **데이터 정규화 및 변환**:
  - `JPYKRW=X` 환율 값은 야후 파이낸스가 1엔 기준으로 데이터를 주기 때문에, 기존 UI 및 모의 사양인 `JPY/KRW (100엔)`과의 정합성을 위해 100을 곱하는 스케일링을 수행한다.
  - `changePercent`는 기존 Mock 데이터 사양과 프론트엔드 호환을 위해 비율이 아닌 백분율(`(price - prev_close) / prev_close * 100`) 단위로 정확하게 매핑한다.
  - `value`, `change`, `changePercent` 수치 항목 중 유한한 숫자가 아니거나(`NaN`, `Infinity` 등) 조회에 실패한 건에 대해서는 안전하게 `None`으로 정규화한다.

## 검토한 대안
- **대안 1: Yahoo Finance v7 Quote API (`/v7/finance/quote?symbols=...`) 일괄 조회**
  - **장점**: 18개 심볼을 쉼표로 연결하여 단 한 번의 HTTP 쿼리로 조회할 수 있어 속도가 매우 빠름.
  - **단점**: 최근 Yahoo Finance 측에서 v7 Quote 엔드포인트에 대해 세션 쿠키, Crumb 토큰 등을 요구하여 단순 `User-Agent` 설정만으로는 `401 Unauthorized` 에러를 반환하며 즉각 차단됨.
  - **기각 사유**: 현업 테스트 결과 v7 API 호출이 완전히 막혀 지속 불가능함.
- **대안 2: 외부 `yfinance` 라이브러리 의존성 추가**
  - **장점**: 라이브러리가 API 우회를 자체 처리해 줌.
  - **단점**: 불필요하게 패키지가 무겁고, 내부적으로 수많은 웹 스크래핑 로직과 다차원 Pandas DataFrame 의존성을 가지고 있어 부하가 크며, 추후 패키지 깨짐이나 차단 위험에 동일하게 직면함.
  - **기각 사유**: "새 외부 라이브러리는 꼭 필요할 때만 추가한다"는 프로젝트 하드 규칙 및 간결성 추구 원칙에 따라, 표준 `urllib.request`를 사용한 v8 Chart API 직접 연동으로 충분히 경량 해결 가능하여 채택하지 않음.

## 변경 파일 계획
- **`src/backend/app/config.py` (수정)**:
  - 야후 파이낸스 연동을 위한 설정 필드 추가 (`yahoo_api_timeout: float = 5.0`, `cache_ttl_seconds: int = 60`) 및 기본값 세팅.
- **`src/backend/app/adapters/yahoo_adapter.py` (신규)**:
  - `YahooMarketDataAdapter` 클래스 구현.
  - 18개 심볼(미국 지수, 한국 지수, 글로벌 지수, 환율) 병렬 호출 기능, 초간단 메모리 캐싱 및 TTL 관리 로직 탑재.
  - `JPYKRW=X` -> JPY/KRW (100엔) 보정 변환 수행.
  - 개별 종목 실패 시 `marketStatus="unavailable"` 및 `value=None` 처리하는 정규화 구현.
- **`src/backend/main.py` (수정)**:
  - 기존 `market_data_adapter = MockMarketDataAdapter()`를 `market_data_adapter = YahooMarketDataAdapter()`로 전격 교체.
- **`tests/backend/test_adapters.py` (수정/추가)**:
  - `YahooMarketDataAdapter` 유닛 테스트 전용 Mock 테스트 추가.
  - 실제 인터넷을 연결하지 않도록 Yahoo API의 원시 JSON 반환 데이터를 mocking하여 성공 시나리오, 부분 실패 시나리오, 네트워크 전체 장애 예외 처리를 검증.
- **`tests/backend/test_api.py` (수정)**:
  - `testMarketDashboardEndpointReturnsDashboardPayload` 등 기존 테스트가 변경된 `YahooMarketDataAdapter` 환경 하에서도 Mocking을 통해 견고하게 성공하도록 수정 및 보강.

## 데이터 / 제어 흐름
- 사용자가 `/api/v1/market/dashboard`에 GET 요청을 보내면 다음과 같은 흐름으로 제어와 데이터가 이동한다.

```
[Client GET /dashboard]
       │
       ▼
[src/backend/main.py] ──(호출)──> [YahooMarketDataAdapter.get_dashboard_data()]
                                        │
                                        ├─── (캐시 유효한가?) ──> [Yes] 캐시 데이터 즉시 반환
                                        │
                                        └─── [No] ──> [ThreadPoolExecutor] 병렬 HTTP 쿼리
                                                             │
                                                     (Yahoo v8 Chart API)
                                                             │
                                                             ▼
                                                [각 심볼별 JSON 응답 파싱]
                                                             │
                                                             ├── JPYKRW=X의 경우 * 100 스케일링
                                                             ├── change, changePercent 계산
                                                             └── NaN/Inf 수치는 None 처리
                                                             │
                                                             ▼
                                                   [캐시 메모리 갱신]
                                                             │
                                                             ▼
[DashboardResponse 검증] <──(반환)────────────── [섹션별 최종 JSON 구성]
       │
       ▼
[Client Response (200 OK)]
```

## 구현 단계 분할
1. **단계 1: 설정 및 신규 어댑터 설계 (`src/backend/app/config.py`, `src/backend/app/adapters/yahoo_adapter.py`)**
   - Yahoo Finance API 조회 타임아웃, 캐시 설정값을 `Settings`에 반영.
   - `YahooMarketDataAdapter`의 전체 골격 작성 및 18개 심볼 매핑 정의.
   - 완료 기준: 컴파일 에러가 없고 인터페이스가 정의됨.
2. **단계 2: 병렬 API 호출 및 메모리 캐싱 로직 상세 구현**
   - `urllib.request`와 `ThreadPoolExecutor`를 결합하여 병렬 호출 루틴을 완성하고, 60초 만료 캐시 로직 적용.
   - `asOf` 시각은 응답의 `regularMarketTime`으로부터 파싱하여 정확한 UTC ISO8601 값으로 변환.
   - `JPYKRW=X` 수치 100배 스케일 변환 및 `changePercent` 백분율 정규화 로직 적용.
   - 완료 기준: 로컬 파이썬 테스트 스크립트 상에서 18개 심볼이 정상 수집 및 캐싱됨.
3. **단계 3: 라우터 연동 및 통합 (`src/backend/main.py`)**
   - API 메인 라우터의 대시보드 데이터 어댑터를 신규 어댑터로 교체.
   - 완료 기준: FastAPI 로컬 기동 시 대시보드 API 호출이 실시간 야후 데이터(2026-05-28 기준 최신 데이터)를 안정적으로 반환함.
4. **단계 4: 테스트 코드 작성 및 검증 (`tests/backend/test_adapters.py`, `tests/backend/test_api.py`)**
   - 실제 HTTP 요청 없이도 동작할 수 있는 Mock 어댑터/API 테스트 코드를 대거 수립.
   - 정상 케이스 및 예외 케이스(네트워크 에러, 일부 항목 누락)에 대한 검증 코드 작성.
   - 완료 기준: `pytest` 실행 시 모든 테스트가 100% 통과함.

## 위험 구간
- **위험 항목: Yahoo Finance API의 잦은 호출로 인한 일시적 차단 (IP Block 또는 Rate Limiting)**
  - **완화 방안**:
    1. 내부 메모리 캐싱 TTL을 60초로 두어, 빈번한 웹 새로고침이나 다중 클라이언트 호출이 발생해도 Yahoo API 호출 주기를 최소화함.
    2. 모든 요청에 유효한 `User-Agent` 값을 부여하여 일반 브라우저 트래픽으로 안정성을 보장함.
- **위험 항목: 외부 API 지연으로 인한 대시보드 API 타임아웃**
  - **완화 방안**:
    1. HTTP 쿼리에 5.0초의 하드 타임아웃을 설정함.
    2. `ThreadPoolExecutor`를 통한 병렬 처리를 함으로써 호출 시간이 누적(Sequential delay)되지 않도록 제어함.
    3. 전체 또는 일부 심볼 로드 실패 시 예외를 포착하여 안전하게 `None` 처리하거나 500 JSON 응답으로 복구함.

## 새 의존성
- **없음** (파이썬 표준 라이브러리 `urllib.request`, `concurrent.futures`, `datetime`, `math`만을 활용하므로 추가 서드파티 패키지가 전혀 없음.)

## 테스트 전략
- **어댑터 단위 테스트 (`tests/backend/test_adapters.py`)**:
  - `YahooMarketDataAdapter`가 성공적으로 API를 파싱하고 캐싱을 작동시키는 가상 mock 테스트.
  - 일부 API 응답이 깨지거나 `NaN`이 포함될 때 정상적으로 `None`으로 치환해주는 경계 조건 테스트.
- **API 연동 테스트 (`tests/backend/test_api.py`)**:
  - API 엔드포인트 `/api/v1/market/dashboard` 호출이 변경된 어댑터 응답을 바르게 포맷하여 반환하는지 검증.
  - 전체 실패 상황 시 FastAPI 라우터가 에러를 잡아서 내부 예외를 가리고 `"Market dashboard data is temporarily unavailable."`라는 안전한 500 에러 메시지를 노출하는지 확인.
- **검증 환경**:
  - `pytest` 명령을 실행하여 모든 테스트를 로컬 격리 환경에서 구동.

## 롤백 / 복구 방향
- 만약 실제 환경 연동 도중 문제가 생기거나 Yahoo Finance v8 API 차단 수준이 강화되어 백엔드가 정지하는 경우, 즉각 `src/backend/main.py` 파일의 어댑터를 기존 `MockMarketDataAdapter`로 변경하여 정적 Mock 데이터 대시보드로 무중단 서비스 롤백을 수행함.

## 실행 승인
- risk_level: medium
- human_gate_required: false
- human_gate_reason: 외부 API 연동이 포함되나, 무인증 공개 API를 사용하며 자체 스레드풀/캐싱 설계로 성능 리스크가 매우 낮고 신규 패키지 설치도 필요 없으므로 하네스 기본값에 따라 바로 자동 개발 단계(PASS)로 진입할 수 있도록 결정함.
- approval_required_before_develop: false

## 스펙 모호점 처리
- 야후 파이낸스 `JPYKRW=X` API의 원시 환율 값은 1엔 단위(예: 9.40)로 반환되나, 기존 Mock 사양 및 한국 시장의 통상적인 100엔 고시 규칙에 따라 100을 곱한 스케일링 값을 노출하기로 정의하여 모호성을 명쾌히 해결함.

## Git 기준점
- base_commit: 352bdef0bfbe60b1093613d3255b66cdb97431e1
- diff_base_command: git diff 352bdef0bfbe60b1093613d3255b66cdb97431e1

## 사용자 확인 사항
- 질문 없음. (추천 Defaults 모드 작동)

## 단계 결과
- status: PASS
- next_stage: 02_develop
- human_gate_required: false
- blocking_reason: 없음
- risk_level: medium
- produced_files:
  - .ai/features/debug/01_plan.md
- changed_files:
- commit_created: false
- commit_message:
- model_mismatch: false
- actual_model: Antigravity
