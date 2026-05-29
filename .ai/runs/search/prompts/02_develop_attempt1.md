# Local Harness Prompt

## Harness Context
- feature_name: search
- pipeline_mode: full
- stage: 02_develop
- preferred_model: Claude
- scheduled_provider: codex
- performance: medium
- output_file: .ai/features/search/02_dev.md
- result_json_file: .ai/features/search/02_dev.result.json
- run_state: .ai/runs/search/run.json
- generated_at: 2026-05-28T16:45:39
- defaults_mode: true
- feature_name_locked: true

## Decision Policy
Use recommended defaults for ambiguous decisions. Do not return NEEDS_USER unless the task is impossible, unsafe, requires credentials/secrets that are not available, or would perform destructive/non-reversible actions. Record all default decisions and their rationale in the stage output.

## Manual Provider Instructions
1. The local harness is executing this prompt with the preferred model when possible.
2. Make the requested file changes directly in the repository.
3. Write the human-readable stage output file exactly at `.ai/features/search/02_dev.md`.
4. Also write the machine-readable stage result JSON exactly at `.ai/features/search/02_dev.result.json`.
5. Do not run `git commit`, `git reset`, `git checkout`, `git rebase`, or `git push`. The local harness owns Git history.
6. This Git ownership rule overrides any preset text that appears to ask the model to create, amend, or push commits.
7. For commit stages, leave the working tree commit-ready and record commit intent in the stage output; the harness will create or amend the commit.
8. If `defaults_mode: true`, prefer recommended defaults over `NEEDS_USER` unless blocked by missing credentials, safety, destructive operations, or impossibility.
9. If the stage needs user input under the decision policy, write both outputs with `status: NEEDS_USER`.
10. If the stage fails, write both outputs with `status: FAIL` and a concrete blocking reason.
11. If `feature_name_locked: true`, keep the existing `feature_name` exactly as provided by the harness. Do not rename or invent a different feature slug.
12. End with a concise summary; the harness will inspect files, not your final message.

## Machine Result JSON Contract
The harness reads `.ai/features/search/02_dev.result.json` first. Keep the `## 단계 결과` section in `.ai/features/search/02_dev.md` for humans, but write this JSON file for the harness.

Required JSON keys:
- status: "PASS", "FAIL", "SKIPPED", or "NEEDS_USER"
- next_stage: next stage id or "done"
- human_gate_required: true or false
- blocking_reason: string, use "" when there is no blocker

Include any extra stage fields that the preset asks for, such as `risk_level`, `harness_commit_required`, `changed_files`, `verification_summary`, or `fix_inputs`.
For PASS or FAIL stages, also include `history_notes` with these arrays when known: `implemented`, `risks`, `future_improvements`, `decisions`, and `unresolved_items`. Use empty arrays for categories with nothing to record. Prefer Korean text for human-facing titles, descriptions, reasons, risks, and decisions when the project context is Korean.

## Project Contract
Source: .ai/project_contract.md

# Project Contract

## Hard Rules
- 모델은 Git commit, amend, reset, checkout, rebase, push를 직접 실행하지 않는다.
- 기존 테스트를 삭제하거나 비활성화하지 않는다.
- 요청 범위를 벗어난 리팩터링, 의존성 추가, 파일 이동은 하지 않는다.

## Project Layout
- 프로덕션 코드는 루트 `src/` 하위에 둔다.
- 테스트 코드는 루트 `tests/` 하위에 둔다.
- 새 테스트 파일을 `src/` 하위에 만들지 않는다.
- 패키지 의존성, 빌드 설정, 실행 설정은 해당 모듈 디렉터리에 두고 루트에는 공유 메타파일만 둔다.

## Architecture
- 외부 데이터 제공자나 서드파티 API 연동은 어댑터 인터페이스 뒤에 두고 비즈니스 로직과 분리한다.

## Code Style
- 새 코드는 같은 디렉터리의 기존 패턴, 네이밍, 파일 구조를 우선 따른다.
- 프로젝트에 이미 명확한 네이밍 관례가 없으면 변수와 함수는 camelCase를 기본으로 한다.
- 함수 이름은 가능하면 동사 또는 동사구로 시작한다. 예: `loadConfig`, `validateInput`, `renderItem`.
- Boolean 값과 Boolean 반환 함수는 `is`, `has`, `can`, `should` 같은 의미 있는 접두사를 사용한다.
- 이벤트 핸들러는 `handle` 또는 기존 프로젝트의 이벤트 네이밍 패턴을 따른다.
- 값을 변환하는 함수는 `to`, `from`, `parse`, `format`, `normalize`처럼 변환 의도가 드러나는 이름을 사용한다.
- 데이터를 가져오는 함수는 `get`, `load`, `fetch`, `read` 중 실제 동작에 맞는 동사를 사용한다.
- 부수효과가 있는 함수는 `save`, `write`, `update`, `delete`, `send`, `create`처럼 변경 의도가 드러나는 동사를 사용한다.
- 구현이 30줄을 넘어가면 함수나 작은 단위로 분리한다.

## Data
- 비율과 백분율처럼 단위가 혼동될 수 있는 값은 파싱 시 단위를 명시적으로 확인하고 중복 변환을 방지한다.

## UX
- 수치 변화 UI는 상승, 하락, 보합, 결측 상태를 구분해 색상과 집계에 반영한다.

## Error Handling
- API 경계에서는 내부 예외를 그대로 노출하지 말고 안전한 JSON 오류 응답으로 변환한다.

## Testing
- 백엔드 API와 비즈니스 로직 테스트는 성공 경로와 함께 입력 오류, 외부 의존성 장애 같은 실패 경로를 포함한다.
- 외부 API 의존 테스트는 실제 네트워크를 사용하지 않고 정상, 누락, 예외 경로를 모두 검증한다.

## Reliability
- 외부 입력, 파일, 네트워크, 프로세스 실행 결과는 실패 가능성을 명시적으로 처리한다.
- API 응답이나 저장소에 수치 데이터를 내보내기 전 NaN/Infinity 등 비유한 값은 안전한 표준 타입으로 정규화한다.
- 외부 리소스를 대량 조회할 때는 캐시, 제한된 동시성, 타임아웃으로 호출량과 지연을 제어한다.
- 일괄 조회는 일부 항목 실패가 전체 실패가 되지 않도록 가능한 데이터와 항목별 결측 상태를 함께 반환한다.


## Original User Request
기존의 대시보드를 메인텝으로하고 이제 설정탭을 추가로 만들어줫으면 좋겠어. 이 설정탭에서의 기능은 주식을 검색하고(한국/미국 주식,etf만) 이 검색한걸 전용탭을 만들어서 추가해놓는거야. 만약 qld라는 종목을 추가했다면 총 탭은 대시보드-qld-설정 이렇게 되겠지. 설정은 항상 가장 마지막에 와야해. 그리고 이 특정 종목을 보는 탭에서는, 이 종목에 대한 자세한 정보가 보였으면해. 시가 종가 등등 엄청 많잖아. 그런거. 그리고 차트까지.

## Previous Stage Outputs
- .ai/features/search/00_spec.md
- .ai/features/search/00_spec.result.json
- .ai/features/search/01_plan.md
- .ai/features/search/01_plan.result.json

## Additional Stage Inputs
- none

## Retry Context
- none

## Current Git Hints
- current_head: da160df675d1918bbcb4b761ad53e043bacbff08
- changed_paths_excluding_runs: [".ai/features/search/"]
- latest_harness_verification: none

---

---
stage: "02_develop"
role: "implementation"
preferred_model: "Claude"
model_policy: "preferred_not_hard_block"
required_inputs:
  - ".ai/features/search/00_spec.md"
  - ".ai/features/search/01_plan.md"
outputs:
  - ".ai/features/search/02_dev.md"
allowed_writes:
  - "production_code"
  - "tests"
  - ".ai/features/search/02_dev.md"
forbidden_writes:
  - ".ai/features/search/00_spec.md"
  - ".ai/features/search/01_plan.md"
human_gate_required: false
commit_policy: "always_commit_stage_02"
commit_owner: "harness"
default_next_stage: "03_review"
---

# 개발 프리셋 (2단계)

## 경로 원칙

- 프로덕션 코드는 루트 `src/` 하위 파일만 의미한다.
- 테스트 코드는 루트 `tests/` 하위 파일만 의미한다.
- 새 테스트 파일은 `tests/` 하위에만 만든다. `src/` 하위에 테스트 파일을 만들지 않는다.
- `requirements.txt`, `run.ps1`, 설정 파일, 의존성 파일, 실행 스크립트 같은 보조 파일도 루트에 만들지 않는다. 필요하면 반드시 `src/` 또는 `tests/` 하위에 둔다.
- `vendor/`, `packages/`, `dist/`, `build/` 등 외부/생성 산출물 디렉터리는 계획/수정/검증 대상에서 제외하고, 필요하면 생성물 또는 외부 산출물로만 기록한다.

## 실행 정책

- 권장 담당 모델은 Claude이다.
- 다른 모델이 이 단계를 실행하더라도 중지하지 않는다.
- 담당 모델이 권장 모델과 다르면 `02_dev.md`의 `## 단계 결과`에 `model_mismatch: true`와 실제 실행 모델을 기록한다.
- 이 단계는 01_plan.md를 기준으로 코드를 구현하고 구현 근거를 남기는 단계이다.
- 계획이 명백히 잘못되었거나 스펙 변경이 필요하면 즉흥적으로 수정하지 말고 `status: NEEDS_USER` 또는 `status: FAIL`로 멈춘다.

---

## 역할

너는 이 프로젝트의 코드 생산 담당이다.
요청받은 기능을 구현하고, 왜 그렇게 구현했는지를 기록으로 남긴다.

---

## 작업 순서

1. `.ai/features/search/00_spec.md`의 목표, 범위, 요구사항, 제외 항목, 위험도를 파악한다.
2. `.ai/features/search/01_plan.md`의 구현 접근 방식, 변경 파일 계획, 구현 단계, 위험 구간, 새 의존성, 테스트 전략, Git 기준점을 파악한다.
3. 작업 시작 전 현재 `HEAD`를 `base_commit`으로 기록한다. 01_plan.md에 `base_commit`이 있으면 그 값을 우선한다.
4. 계획대로 구현한다.
5. 계획에 없는 작은 결정은 코드베이스 컨벤션에 맞춰 합리적으로 결정하고 `02_dev.md`에 기록한다.
6. 계획과 충돌하는 변경이 필요하면 구현을 멈추고 `계획 변경 필요` 블록을 작성한다.
7. 기능 구현과 함께 계획된 테스트를 작성한다.
8. 가능한 테스트를 실행하고 결과를 기록한다.
9. 구현이 끝나면 `.ai/features/search/02_dev.md`를 작성한다.
10. 첫 번째 커밋에 포함되어야 할 파일 범위를 `02_dev.md`에 기록한다. 범위에는 반드시 `00_spec.md`, `01_plan.md`, `02_dev.md`, 구현 코드, 구현 테스트가 포함되어야 한다.
11. `git commit`, `git reset`, `git checkout`, `git rebase`, `git push`를 실행하지 않는다. 실제 커밋은 하네스가 만든다.
12. 하네스가 커밋할 수 있도록 워킹트리를 커밋 가능한 상태로 남기고, `harness_commit_required: true`와 추천 커밋 메시지를 기록한다. 추천 커밋 메시지는 `search[YYYYMMDD-hhmmss][02_develop]` 포맷을 사용한다.
13. 커밋 가능한 상태를 만들 수 없으면 이유를 기록하고 `status: FAIL` 또는 `status: NEEDS_USER`로 멈춘다.
14. 이 단계 산출물 안에 커밋 SHA를 기록하려고 하지 않는다. 커밋 SHA는 하네스가 커밋한 뒤에 생기므로 이 단계 산출물에는 정확히 적을 수 없다.

---

## 계획 변경 필요 형식

계획을 그대로 수행할 수 없으면 `.ai/features/search/02_dev.md`에 아래 블록을 작성하고 멈춘다.

```markdown
## 계획 변경 필요
- status: NEEDS_USER
- 발견한 문제:
- 기존 계획:
- 필요한 변경:
- 추천안:
- 대안:
- 사용자가 답하면 재개할 단계: 01_plan 또는 02_develop
```

---

## 구현 원칙

- 01_plan.md의 계획을 우선한다.
- 00_spec.md와 01_plan.md는 이 단계에서 수정하지 않는다.
- 계획이 실제 코드와 맞지 않으면 코드를 고쳐 계획에 맞추거나, 불가능하면 `계획 변경 필요` 블록을 작성하고 멈춘다.
- 스펙 또는 계획 자체의 변경이 필요하면 `next_stage: 01_plan` 또는 `00_specify`로 되돌린다.
- 기존 프로젝트의 디렉토리 구조, 네이밍 컨벤션, 코드 스타일을 따른다.
- 이 단계는 기능당 고정 커밋 3개 중 첫 번째 커밋을 하네스가 만들 수 있게 준비하는 단계이다.
- 모델은 직접 커밋하지 않고, 하네스가 0단계와 1단계 산출물, 2단계 산출물, 구현 코드, 구현 테스트를 첫 번째 커밋에 포함할 수 있게 변경을 남긴다.
- 외부 라이브러리는 01_plan.md에 사전 합의된 경우에만 추가한다.
- 에러 핸들링과 엣지 케이스를 고려한다.
- 01_plan.md의 위험 구간 항목은 빠짐없이 대응한다.
- 기능 구현과 함께 해당 기능의 테스트 코드를 루트 `tests/` 하위에 작성한다.
- 기존 테스트를 삭제하거나 비활성화하지 않는다.
- 기능 범위를 벗어난 리팩토링을 하지 않는다.

---

## 기록 양식

구현 완료 후 `.ai/features/search/02_dev.md`에 아래 형식으로 작성한다.

```markdown
# 02_dev - search

작성: [실제 실행 모델]
일시: YYYY-MM-DD

## 기능 목표
- 이 기능이 무엇을 하는지 한두 줄로 요약

## 변경 파일
- .ai/features/search/00_spec.md (입력 / 변경 금지)
- .ai/features/search/01_plan.md (입력 / 변경 금지)
- .ai/features/search/02_dev.md (신규 / 수정)
- src/path/to/file.py (신규 / 수정 / 삭제)
- src/path/to/another.py (신규 / 수정 / 삭제)

## 구현 내용
- 무엇을 어떻게 구현했는지 서술

## 왜 이렇게 구현했는가
- 이 방식을 선택한 이유
- 고려했지만 채택하지 않은 대안이 있다면 그 이유
- 의도적으로 생략하거나 단순화한 부분이 있다면 그 이유
- 계획에 없는 작은 결정을 한 경우 그 판단과 이유

## 새로 추가한 의존성
- 없음
- 또는 패키지명: 추가 이유

## 테스트
- 작성한 테스트 파일 경로 (`tests/` 하위)
- 테스트가 커버하는 범위 요약
- 실행한 테스트 명령
- 테스트 실행 결과
- 의도적으로 테스트하지 않은 부분이 있다면 그 이유

## 알려진 한계 / 추후 개선 사항
- 현재 구현의 한계점
- 다음 단계에서 보완이 필요한 부분

## Git 정보
- base_commit:
- harness_commit_required: true
- commit_created_by_model: false
- commit_message_suggestion: search[YYYYMMDD-hhmmss][02_develop]
- commit_scope:
  - .ai/features/search/02_dev.md
  - 구현 코드와 구현 테스트
- pre_commit_diff_command: git diff [base_commit]
- changed_files:
- harness_commit_blocking_reason:

## 단계 결과
- status: PASS / NEEDS_USER / FAIL
- next_stage: 03_review
- human_gate_required: false
- blocking_reason: 없음
- risk_level: low / medium / high
- produced_files:
  - .ai/features/search/02_dev.md
- changed_files:
- harness_commit_required: true
- commit_created_by_model: false
- commit_message_suggestion:
- test_commands:
- model_mismatch: false
- actual_model:
```

---

## 금지 사항

- 01_plan.md를 읽지 않은 채 구현을 시작하지 않는다.
- 01_plan.md의 계획을 사용자 동의 없이 크게 변경하지 않는다.
- 00_spec.md 또는 01_plan.md를 직접 수정하지 않는다.
- 기존 테스트를 삭제하거나 비활성화하지 않는다.
- 기능 범위를 벗어난 리팩토링을 하지 않는다.
- `git commit`, `git reset`, `git checkout`, `git rebase`, `git push`를 실행하지 않는다.
