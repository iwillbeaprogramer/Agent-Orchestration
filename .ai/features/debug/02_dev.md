# 02_dev - debug

작성: Codex
일시: 2026-05-28

## 기능 목표
- `/api/v1/market/dashboard`가 정적 mock 값이 아니라 실행 시점 기준 Yahoo Finance Chart API의 최신 시장 지수와 환율 값을 반환하도록 구현했다.
- 응답 스키마와 섹션 id는 유지하고, 부분 실패 항목은 `unavailable` 상태와 `null` 수치로 안전하게 표현한다.

## 변경 파일
- .ai/features/debug/00_spec.md (입력 / 변경 금지)
- .ai/features/debug/01_plan.md (입력 / 변경 금지)
- .ai/features/debug/02_dev.md (신규)
- .ai/features/debug/02_dev.result.json (신규)
- src/backend/app/config.py (수정)
- src/backend/app/adapters/yahoo_adapter.py (신규)
- src/backend/main.py (수정)
- tests/backend/test_adapters.py (수정)
- tests/backend/test_api.py (수정)

## 구현 내용
- `YahooMarketDataAdapter`를 추가해 Yahoo Finance v8 Chart API에서 18개 지수/환율 항목을 병렬 조회하도록 했다.
- 60초 인메모리 캐시와 5초 HTTP 타임아웃 설정을 추가했다.
- `regularMarketPrice`, `previousClose`, `regularMarketTime`, `marketState`를 파싱해 `value`, `change`, `changePercent`, `asOf`, `marketStatus`를 채운다.
- `JPYKRW=X`는 기존 UI 표기와 맞게 100엔 기준으로 스케일링했다.
- 개별 항목 실패는 `source: yahoo-finance-v8:unavailable`, `marketStatus: unavailable`, 수치 `null`로 반환하고, 모든 항목이 실패하면 API 경계에서 안전한 500 JSON 오류가 되도록 예외를 발생시킨다.
- 기본 API 어댑터를 `MockMarketDataAdapter`에서 `YahooMarketDataAdapter`로 교체했다.

## 왜 이렇게 구현했는가
- 01_plan.md가 지정한 Yahoo Finance v8 Chart API, `urllib.request`, `ThreadPoolExecutor`, 단기 캐시 방식을 그대로 따랐다.
- 새 외부 의존성은 추가하지 않았다. 공개 API 호출과 테스트 가능한 fetcher 주입만으로 범위를 좁혔다.
- 섹션 id와 기존 표시명은 유지했다. 기존 프론트엔드와 테스트가 id/명칭에 의존할 수 있기 때문이다.
- 전체 실패 시 오래된 mock을 최신 데이터처럼 보여주지 않도록 500 오류로 처리했다.
- 계획에 없던 작은 결정: Yahoo path segment의 `^`, `=` 문자를 `quote(..., safe="")`로 인코딩했다. 실제 호출 안정성과 테스트 재현성을 높이기 위한 처리다.

## 새로 추가한 의존성
- 없음

## 테스트
- 작성/수정한 테스트 파일:
  - tests/backend/test_adapters.py
  - tests/backend/test_api.py
- 커버 범위:
  - Yahoo 응답 파싱, 18개 항목 조회, change/changePercent 계산, JPY/KRW 100엔 스케일링
  - 인메모리 캐시가 원본 데이터를 외부 변경으로부터 보호하는지 검증
  - 일부 항목 실패 시 `unavailable` 처리
  - provider 응답에 최신 가격이 누락된 malformed 항목의 `unavailable` 처리
  - 전체 provider 실패 시 어댑터 예외와 API의 안전한 500 오류 응답
  - API 테스트가 실제 네트워크에 의존하지 않도록 stub 어댑터 사용
- 실행한 테스트 명령:
  - `python -m pytest -q`
  - 실제 Yahoo 연동 스모크 스크립트: `YahooMarketDataAdapter(cache_ttl_seconds=0).get_dashboard_data()`
- 테스트 실행 결과:
  - `14 passed in 0.56s`
  - 실제 연동 스모크 결과: 18개 중 18개 항목 값 수집 성공
- 의도적으로 테스트하지 않은 부분:
  - Yahoo Finance 자체의 장중/장마감 데이터 정확성은 외부 제공자 책임이므로 로컬 단위 테스트에서는 고정 payload로 검증했다.

## 알려진 한계 / 추후 개선 사항
- Yahoo Finance 공개 엔드포인트는 인증이 없지만 차단 또는 응답 형식 변경 가능성이 있다.
- 캐시는 프로세스 메모리 기반이므로 서버 재시작 시 초기화된다.
- provider별 장애율, 응답 시간, 마지막 성공 시각 같은 관측 지표는 아직 없다.

## Git 정보
- base_commit: 352bdef0bfbe60b1093613d3255b66cdb97431e1
- harness_commit_required: true
- commit_created_by_model: false
- commit_message_suggestion: debug[20260528-162732][02_develop]
- commit_scope:
  - .ai/features/debug/00_spec.md
  - .ai/features/debug/00_spec.result.json
  - .ai/features/debug/01_plan.md
  - .ai/features/debug/01_plan.result.json
  - .ai/features/debug/02_dev.md
  - .ai/features/debug/02_dev.result.json
  - src/backend/app/config.py
  - src/backend/app/adapters/yahoo_adapter.py
  - src/backend/main.py
  - tests/backend/test_adapters.py
  - tests/backend/test_api.py
- pre_commit_diff_command: git diff 352bdef0bfbe60b1093613d3255b66cdb97431e1
- changed_files:
  - .ai/features/debug/02_dev.md
  - .ai/features/debug/02_dev.result.json
  - src/backend/app/config.py
  - src/backend/app/adapters/yahoo_adapter.py
  - src/backend/main.py
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
  - .ai/features/debug/02_dev.md
  - .ai/features/debug/02_dev.result.json
- changed_files:
  - .ai/features/debug/02_dev.md
  - .ai/features/debug/02_dev.result.json
  - src/backend/app/config.py
  - src/backend/app/adapters/yahoo_adapter.py
  - src/backend/main.py
  - tests/backend/test_adapters.py
  - tests/backend/test_api.py
- harness_commit_required: true
- commit_created_by_model: false
- commit_message_suggestion: debug[20260528-162732][02_develop]
- test_commands:
  - python -m pytest -q
  - YahooMarketDataAdapter 실제 연동 스모크 스크립트
- model_mismatch: true
- actual_model: Codex
