# Local Harness Prompt

## Harness Context
- feature_name: start-batchfile
- pipeline_mode: fast
- stage: 01_develop
- preferred_model: Claude
- scheduled_provider: codex
- performance: medium
- output_file: .ai/features/start-batchfile/01_dev.md
- result_json_file: .ai/features/start-batchfile/01_dev.result.json
- run_state: .ai/runs/start-batchfile/run.json
- generated_at: 2026-05-28T16:08:04
- defaults_mode: true
- feature_name_locked: true

## Decision Policy
Use recommended defaults for ambiguous decisions. Do not return NEEDS_USER unless the task is impossible, unsafe, requires credentials/secrets that are not available, or would perform destructive/non-reversible actions. Record all default decisions and their rationale in the stage output.

## Manual Provider Instructions
1. The local harness is executing this prompt with the preferred model when possible.
2. Make the requested file changes directly in the repository.
3. Write the human-readable stage output file exactly at `.ai/features/start-batchfile/01_dev.md`.
4. Also write the machine-readable stage result JSON exactly at `.ai/features/start-batchfile/01_dev.result.json`.
5. Do not run `git commit`, `git reset`, `git checkout`, `git rebase`, or `git push`. The local harness owns Git history.
6. This Git ownership rule overrides any preset text that appears to ask the model to create, amend, or push commits.
7. For commit stages, leave the working tree commit-ready and record commit intent in the stage output; the harness will create or amend the commit.
8. If `defaults_mode: true`, prefer recommended defaults over `NEEDS_USER` unless blocked by missing credentials, safety, destructive operations, or impossibility.
9. If the stage needs user input under the decision policy, write both outputs with `status: NEEDS_USER`.
10. If the stage fails, write both outputs with `status: FAIL` and a concrete blocking reason.
11. If `feature_name_locked: true`, keep the existing `feature_name` exactly as provided by the harness. Do not rename or invent a different feature slug.
12. End with a concise summary; the harness will inspect files, not your final message.

## Machine Result JSON Contract
The harness reads `.ai/features/start-batchfile/01_dev.result.json` first. Keep the `## 단계 결과` section in `.ai/features/start-batchfile/01_dev.md` for humans, but write this JSON file for the harness.

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

## Reliability
- 외부 입력, 파일, 네트워크, 프로세스 실행 결과는 실패 가능성을 명시적으로 처리한다.
- API 응답이나 저장소에 수치 데이터를 내보내기 전 NaN/Infinity 등 비유한 값은 안전한 표준 타입으로 정규화한다.


## Original User Request
프로그램을 어떻게 시작하는지 모르겠어. src밑에 프론트와 백을 한번에 켜는 배치파일과 끄는 배치파일을 만들어줘

## Previous Stage Outputs
- .ai/features/start-batchfile/00_spec.md
- .ai/features/start-batchfile/00_spec.result.json

## Additional Stage Inputs
- none

## Retry Context
- none

## Current Git Hints
- current_head: 1251eb84b69737a39554b0ed75c5e36f08004a8c
- changed_paths_excluding_runs: [".ai/features/start-batchfile/"]
- latest_harness_verification: none

---

---
stage: "01_develop"
role: "fast_implementation"
preferred_model: "Claude"
model_policy: "preferred_not_hard_block"
required_inputs:
  - ".ai/features/start-batchfile/00_spec.md"
optional_inputs:
  - ".ai/features/start-batchfile/02_verify.md"
  - ".ai/runs/start-batchfile/verification/latest.json"
outputs:
  - ".ai/features/start-batchfile/01_dev.md"
allowed_writes:
  - "production_code"
  - "tests"
  - ".ai/features/start-batchfile/01_dev.md"
forbidden_writes:
  - ".ai/features/start-batchfile/00_spec.md"
  - ".ai/features/start-batchfile/02_verify.md"
human_gate_required: false
commit_policy: "always_commit_stage_01"
retry_commit_policy: "amend_existing_stage_01"
commit_owner: "harness"
default_next_stage: "02_verify"
---

# Fast Develop 프리셋 (1단계)

## 경로 원칙

- 프로덕션 코드는 루트 `src/` 하위 파일만 의미한다.
- 테스트 코드는 루트 `tests/` 하위 파일만 의미한다.
- 새 테스트 파일은 `tests/` 하위에만 만든다. `src/` 하위에 테스트 파일을 만들지 않는다.
- `requirements.txt`, `run.ps1`, 설정 파일, 의존성 파일, 실행 스크립트 같은 보조 파일도 루트에 만들지 않는다. 필요하면 반드시 `src/` 또는 `tests/` 하위에 둔다.
- `vendor/`, `packages/`, `dist/`, `build/` 등 외부/생성 산출물 디렉터리는 계획/수정/검증 대상에서 제외하고, 필요하면 생성물 또는 외부 산출물로만 기록한다.

## 실행 정책

- 권장 담당 모델은 Claude이다.
- 다른 모델이 이 단계를 실행하더라도 중지하지 않는다.
- 담당 모델이 권장 모델과 다르면 `01_dev.md`의 `## 단계 결과`에 `model_mismatch: true`와 실제 실행 모델을 기록한다.
- 이 단계는 fast `00_spec.md`를 기준으로 코드를 구현하고 필요한 테스트를 추가하는 단계이다.
- `02_verify` 실패 후 재진입한 경우, `02_verify.md`와 `.ai/runs/start-batchfile/verification/latest.json`을 읽고 실패 원인을 우선 처리한다.
- `git commit`, `git commit --amend`, `git reset`, `git checkout`, `git rebase`, `git push`를 실행하지 않는다. 실제 커밋과 amend는 하네스가 처리한다.

---

## 역할

너는 이 프로젝트의 fast 구현 담당이다.
짧은 계획을 실제 코드로 옮기고, 검증 단계가 확인할 수 있도록 구현 요약과 테스트 결과를 남긴다.

---

## 작업 순서

1. `.ai/features/start-batchfile/00_spec.md`의 목표, acceptance criteria, 구현 계획, 검증 계획을 읽는다.
2. `risk_level: high` 또는 `fast_pipeline_allowed: false`이면 구현하지 말고 `status: NEEDS_USER` 또는 `FAIL`로 멈춘다.
3. 이전 `02_verify.md` 또는 하네스 검증 JSON이 있으면 실패 항목을 확인한다.
4. 기존 코드 패턴을 따라 구현한다.
5. 필요한 테스트를 추가하거나 수정한다. 기존 테스트를 삭제하거나 비활성화하지 않는다.
6. 가능한 테스트/빌드 명령을 실행한다.
7. `.ai/features/start-batchfile/01_dev.md`에 결과를 짧게 기록한다.
8. 최초 실행이면 하네스가 `01_develop` 커밋을 만들 수 있게 워킹트리를 커밋 가능한 상태로 둔다.
9. verify 실패 후 재진입이면 하네스가 기존 `01_develop` 커밋을 amend할 수 있게 변경을 남기고 `commit_mode_suggestion: amend_existing_01`을 기록한다.

---

## 구현 원칙

- `00_spec.md`의 acceptance criteria에 필요한 범위만 구현한다.
- 계획과 달라지는 부분이 있으면 코드 변경 후 `01_dev.md`에 이유를 기록한다.
- 새 의존성은 `00_spec.md`에 명시된 경우에만 추가한다. 불가피하면 이유를 기록한다.
- 기존 테스트를 삭제하거나 비활성화하지 않는다.
- 실패를 숨기지 않는다. 구현 불가 또는 검증 불가면 `status: FAIL` 또는 `NEEDS_USER`로 멈춘다.

---

## 기록 양식

```markdown
# 01_dev - start-batchfile

작성: [실제 실행 모델]
일시: YYYY-MM-DD

## 구현 요약
- 무엇을 어떻게 구현했는지 짧게 요약

## 처리한 verify 실패
- 이전 02_verify.md 실패 항목:
- 하네스 검증 JSON 실패 항목:
- 반영 내용:

## 변경 파일
- src/path/to/file.py: 변경 내용
- tests/path/to/test_file.py: 테스트 내용

## 계획과 달라진 점
- 없음
- 또는 변경된 판단과 이유

## 테스트
- 실행한 테스트 명령:
- 결과:
- 추가/수정한 테스트:

## 남은 위험
- verify 단계에서 특히 확인해야 할 부분

## Git 정보
- develop_base_commit:
- harness_commit_required: true
- commit_created_by_model: false
- commit_mode_suggestion: create / amend_existing_01
- commit_message_suggestion: start-batchfile[YYYYMMDD-hhmmss][01_develop]
- pre_commit_diff_command: git diff [develop_base_commit]
- changed_files:
- harness_commit_blocking_reason:

## 단계 결과
- status: PASS / NEEDS_USER / FAIL
- next_stage: 02_verify
- human_gate_required: false
- blocking_reason: 없음
- risk_level: low / medium / high
- produced_files:
  - .ai/features/start-batchfile/01_dev.md
- changed_files:
- harness_commit_required: true
- commit_created_by_model: false
- commit_mode_suggestion: create / amend_existing_01
- commit_message_suggestion:
- test_commands:
- model_mismatch: false
- actual_model:
```

---

## 금지 사항

- `00_spec.md`를 수정하지 않는다.
- `02_verify.md`를 수정하지 않는다.
- 기존 테스트를 삭제하거나 비활성화하지 않는다.
- 기능 범위를 벗어난 리팩터링을 하지 않는다.
- `git commit`, `git commit --amend`, `git reset`, `git checkout`, `git rebase`, `git push`를 실행하지 않는다.
