# 04_fix - project-initialize

작성: Codex
일시: 2026-05-28

## 입력으로 처리한 지적
- 03_review.md must_fix:
  - MAJOR: `changePercent`가 0 또는 null인 항목이 상승(`positive`) UI로 표시되는 문제
  - MAJOR: 백엔드 API 실패 경로 테스트 누락
- 03_review.md should_consider:
  - MINOR: `/api/v1/market/dashboard` 라우터의 어댑터 예외 방어 부족
  - MINOR: 등락값(`change`) 양수 표시 시 `+` 기호 누락
  - NIT: `MarketItemCard.jsx`의 의미 없는 조건식 제거
  - NIT: Python 함수명 PEP 8 정렬 검토
- 05_verify.md 실패 항목: 없음
- 05_verify.md가 추가한 테스트 파일: 없음

## 수용한 항목
- 출처: 03_review
- severity: MAJOR
- 지적 내용 요약: 보합(0) 또는 값 없음(null/undefined/NaN) 상태가 상승 색상과 상승 집계로 처리됨
- 수정한 파일과 변경 내용:
  - `src/frontend/src/components/MarketItemCard.jsx`: 상승/하락/중립 판정 로직을 분리하고 0/null/NaN을 `neutral`로 처리
  - `src/frontend/src/App.jsx`: 요약 집계에 `neutral`을 추가하고 0/null/NaN을 상승 집계에서 제외
  - `src/frontend/src/index.css`: 중립 카드 라인과 중립 텍스트 색상을 추가하고, 상승 텍스트 스타일을 `.positive` 카드에만 적용
- 왜 수용했는가: 실제 데이터 결측이나 보합 상태를 상승으로 오인하게 만드는 사용자-facing UI 버그이므로 수정 필요

- 출처: 03_review
- severity: MAJOR
- 지적 내용 요약: 백엔드 어댑터 실패 경로 테스트 누락
- 수정한 파일과 변경 내용:
  - `tests/backend/test_api.py`: 어댑터가 예외를 던질 때 API가 안전한 500 JSON 응답을 반환하는 테스트 추가
- 왜 수용했는가: 외부 데이터 제공자 연동으로 교체될 수 있는 경계이므로 실패 경로 회귀 테스트가 필요

- 출처: 03_review
- severity: MINOR
- 지적 내용 요약: 백엔드 API 라우터에서 어댑터 예외를 방어하지 않음
- 수정한 파일과 변경 내용:
  - `src/backend/main.py`: 어댑터 조회와 Pydantic 검증을 `try-except`로 감싸고 내부 예외는 로그로 남긴 뒤 안전한 `HTTPException(500)` 응답으로 변환
- 왜 수용했는가: 테스트만 추가하면 실제 실패 처리가 개선되지 않으므로 라우터 방어 로직도 함께 필요

- 출처: 03_review
- severity: MINOR
- 지적 내용 요약: 등락값(`change`) 양수에 `+` 기호가 없어 등락률 표시와 일관성이 떨어짐
- 수정한 파일과 변경 내용:
  - `src/frontend/src/components/MarketItemCard.jsx`: `formatSignedNumber`를 추가해 양수 등락값에 `+` 기호 표시
- 왜 수용했는가: 시장 대시보드에서 등락값과 등락률의 시각 표현 일관성을 높이는 낮은 위험의 개선

- 출처: 03_review
- severity: NIT
- 지적 내용 요약: `maximumFractionDigits: currency === 'KRW' ? 2 : 2` 조건식이 의미 없음
- 수정한 파일과 변경 내용:
  - `src/frontend/src/components/MarketItemCard.jsx`: 조건식을 `maximumFractionDigits: 2`로 단순화
- 왜 수용했는가: 동작 변화 없이 가독성을 개선하는 지적

## 거부한 항목
- 출처: 03_review
- severity: NIT
- 지적 내용 요약: 백엔드 Python 함수명을 PEP 8 snake_case로 일원화할지 검토
- 왜 수용하지 않았는가: 프로젝트 계약에 명확한 네이밍 관례가 없으면 camelCase를 기본값으로 둔다고 되어 있고, 현재 API 스키마 필드도 camelCase를 사용한다.
- 거부해도 문제가 없는 근거: 기능 버그나 테스트 결함이 아니며, 함수명 변경은 이번 리뷰 must_fix 범위를 벗어난 스타일 정리이다. 추후 프로젝트 전반 네이밍 정책을 정하면 별도 정리로 처리하는 것이 적절하다.

## 보류한 항목
- 없음

## 사용자 판단 요청 항목
- 없음

## 추가 변경 사항
- 요약 스트립에 `보합/기타` 카운터를 추가했다.
- 이유: 카드 단위의 중립 표시만으로는 전체 집계에서 0/null 데이터가 누락될 수 있어, 상승/하락과 별도 집계가 필요했다.

## 변경 파일 목록
- `src/backend/main.py`: 시장 대시보드 라우터 예외 처리 및 로깅 추가
- `src/frontend/src/App.jsx`: 상승/하락/중립 요약 집계 보완
- `src/frontend/src/components/MarketItemCard.jsx`: 중립 tone 판정, 양수 등락값 `+` 표시, 불필요 조건식 제거
- `src/frontend/src/index.css`: 중립 카드/텍스트 스타일 추가, 상승 텍스트 범위 축소
- `tests/backend/test_api.py`: 어댑터 실패 시 안전한 500 응답 테스트 추가

## 테스트
- 실행한 테스트 명령:
  - `python -m pytest tests/backend`
  - `npm run build` (`src/frontend`)
- 결과:
  - `python -m pytest tests/backend`: 7 passed
  - `npm run build`: PASS
- 추가한 테스트:
  - `testMarketDashboardEndpointReturnsSafeErrorWhenAdapterFails`

## Git 정보
- fix_base_commit: a453cf72dee482542a4b004760eea8383bfb2369
- harness_commit_required: true
- commit_created_by_model: false
- commit_mode_suggestion: create
- commit_message_suggestion: project-initialize[20260528-155254][04_fix]
- no_code_changes: false
- no_code_changes_reason:
- pre_commit_diff_command: git diff a453cf72dee482542a4b004760eea8383bfb2369
- changed_files:
  - `src/backend/main.py`
  - `src/frontend/src/App.jsx`
  - `src/frontend/src/components/MarketItemCard.jsx`
  - `src/frontend/src/index.css`
  - `tests/backend/test_api.py`
  - `.ai/features/project-initialize/04_fix.md`
  - `.ai/features/project-initialize/04_fix.result.json`
- harness_commit_blocking_reason: 없음

## 단계 결과
- status: PASS
- next_stage: 05_verify
- human_gate_required: false
- blocking_reason: 없음
- risk_level: medium
- produced_files:
  - .ai/features/project-initialize/04_fix.md
  - .ai/features/project-initialize/04_fix.result.json
- changed_files:
  - src/backend/main.py
  - src/frontend/src/App.jsx
  - src/frontend/src/components/MarketItemCard.jsx
  - src/frontend/src/index.css
  - tests/backend/test_api.py
  - .ai/features/project-initialize/04_fix.md
  - .ai/features/project-initialize/04_fix.result.json
- harness_commit_required: true
- commit_created_by_model: false
- commit_mode_suggestion: create
- commit_message_suggestion: project-initialize[20260528-155254][04_fix]
- test_commands:
  - python -m pytest tests/backend
  - npm run build
- model_mismatch: true
- actual_model: Codex
