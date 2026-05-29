# 04_fix - search

작성: Codex
일시: 2026-05-29

## 입력으로 처리한 지적
- 03_review.md must_fix: 없음
- 03_review.md should_consider: `YahooMarketDataAdapter`의 `_lookup_cache`가 조회되지 않는 만료 항목을 계속 보관할 수 있어 메모리 사용량이 점진적으로 증가할 수 있음
- 05_verify.md 실패 항목: 없음
- 05_verify.md가 추가한 테스트 파일: 없음

## 수용한 항목
- 출처: 03_review
- severity: MINOR
- 지적 내용 요약: 검색/상세 조회 캐시인 `_lookup_cache`에 항목 수 제한과 만료 항목 정리 로직이 없어 장시간 실행 시 메모리 누적 가능성이 있음
- 수정한 파일과 변경 내용:
  - `src/backend/app/adapters/yahoo_adapter.py`: lookup 캐시 최대 항목 수 기본값 128 추가, 캐시 쓰기 시 만료 항목 정리, 한도 초과 시 가장 먼저 만료될 항목 제거
  - `tests/backend/test_adapters.py`: lookup 캐시 한도 초과 시 오래된 검색 캐시가 제거되는 회귀 테스트 추가
- 왜 수용했는가: 외부 검색어와 상세 조회 키는 사용 패턴에 따라 계속 늘 수 있고, 제한된 캐시 정책은 기존 API 동작을 바꾸지 않으면서 장시간 프로세스 안정성을 높임

## 거부한 항목
- 출처: 03_review
- severity: NIT
- 지적 내용 요약: 주가/차트 숫자 포맷을 통화별로 더 정교하게 표시하는 개선
- 왜 수용하지 않았는가: 기능 버그가 아니며 현재 단계의 핵심 리뷰 입력은 캐시 메모리 완화임. 프론트엔드 표시 정책 변경은 스냅샷/시각 검증 없이 함께 넣으면 표시 회귀 범위가 커질 수 있음
- 거부해도 문제가 없는 근거: 현재 UI는 숫자와 통화 코드를 함께 보여 주어 USD/KRW 구분은 가능하고, 03_review에서도 optional 항목으로 분류됨

- 출처: 03_review
- severity: NIT
- 지적 내용 요약: 거래소 상수를 어댑터 본체에서 별도 설정 모듈로 이동 권장
- 왜 수용하지 않았는가: 현재 스펙은 한국/미국 주식 및 ETF로 범위가 고정되어 있고, 별도 설정 파일 이동은 동작 개선 없이 변경 범위를 넓힘
- 거부해도 문제가 없는 근거: 상수는 해당 Yahoo 어댑터의 필터링 구현 세부사항이며, 다른 어댑터나 API 계약에 노출되지 않음

## 보류한 항목
- 없음

## 사용자 판단 요청 항목
- 없음

## 추가 변경 사항
- 없음

## 변경 파일 목록
- `src/backend/app/adapters/yahoo_adapter.py`: lookup 캐시 항목 수 제한, 만료 정리, 초과 항목 eviction 추가
- `tests/backend/test_adapters.py`: lookup 캐시 eviction 회귀 테스트 추가
- `.ai/features/search/04_fix.md`: 04_fix 처리 기록 추가
- `.ai/features/search/04_fix.result.json`: 하네스용 단계 결과 JSON 추가

## 테스트
- 실행한 테스트 명령:
  - `python -m pytest tests -q`
  - `$env:TMP/.TEMP`를 워크스페이스 `.pytest-tmp`로 지정한 뒤 `python -m pytest tests -q`
  - `npm run build` (`src/frontend`)
- 결과:
  - 첫 `python -m pytest tests -q`는 코드 테스트 23개 통과 후 Windows 기본 임시 디렉터리 `C:\Users\SuHyun.Kim\AppData\Local\Temp\pytest-of-SuHyun.Kim` 접근 권한 문제로 하네스 테스트 fixture 생성이 실패함
  - 워크스페이스 임시 디렉터리 지정 재실행: `27 passed in 0.65s`
  - Vite production build 성공
- 추가한 테스트:
  - `testYahooAdapterLimitsLookupCacheSize`

## Git 정보
- fix_base_commit: 68a86c7f146ade5d2989b477cfd39f452eb1cf47
- harness_commit_required: true
- commit_created_by_model: false
- commit_mode_suggestion: create
- commit_message_suggestion: search[20260529-095105][04_fix]
- no_code_changes: false
- no_code_changes_reason:
- pre_commit_diff_command: git diff 68a86c7f146ade5d2989b477cfd39f452eb1cf47
- changed_files:
  - src/backend/app/adapters/yahoo_adapter.py
  - tests/backend/test_adapters.py
  - .ai/features/search/04_fix.md
  - .ai/features/search/04_fix.result.json
- harness_commit_blocking_reason:

## 단계 결과
- status: PASS
- next_stage: 05_verify
- human_gate_required: false
- blocking_reason: 없음
- risk_level: low
- produced_files:
  - .ai/features/search/04_fix.md
  - .ai/features/search/04_fix.result.json
- changed_files:
  - src/backend/app/adapters/yahoo_adapter.py
  - tests/backend/test_adapters.py
  - .ai/features/search/04_fix.md
  - .ai/features/search/04_fix.result.json
- harness_commit_required: true
- commit_created_by_model: false
- commit_mode_suggestion: create
- commit_message_suggestion: search[20260529-095105][04_fix]
- test_commands:
  - python -m pytest tests -q
  - npm run build
- model_mismatch: true
- actual_model: Codex
