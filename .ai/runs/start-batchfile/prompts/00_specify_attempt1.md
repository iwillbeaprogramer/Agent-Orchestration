# Local Harness Prompt

## Harness Context
- feature_name: start-batchfile
- pipeline_mode: fast
- stage: 00_specify
- preferred_model: Antigravity
- scheduled_provider: agy
- performance: medium
- output_file: .ai/features/start-batchfile/00_spec.md
- result_json_file: .ai/features/start-batchfile/00_spec.result.json
- run_state: .ai/runs/start-batchfile/run.json
- generated_at: 2026-05-28T16:07:24
- defaults_mode: true
- feature_name_locked: true

## Decision Policy
Use recommended defaults for ambiguous decisions. Do not return NEEDS_USER unless the task is impossible, unsafe, requires credentials/secrets that are not available, or would perform destructive/non-reversible actions. Record all default decisions and their rationale in the stage output.

## Manual Provider Instructions
1. The local harness is executing this prompt with the preferred model when possible.
2. Make the requested file changes directly in the repository.
3. Write the human-readable stage output file exactly at `.ai/features/start-batchfile/00_spec.md`.
4. Also write the machine-readable stage result JSON exactly at `.ai/features/start-batchfile/00_spec.result.json`.
5. Do not run `git commit`, `git reset`, `git checkout`, `git rebase`, or `git push`. The local harness owns Git history.
6. This Git ownership rule overrides any preset text that appears to ask the model to create, amend, or push commits.
7. For commit stages, leave the working tree commit-ready and record commit intent in the stage output; the harness will create or amend the commit.
8. If `defaults_mode: true`, prefer recommended defaults over `NEEDS_USER` unless blocked by missing credentials, safety, destructive operations, or impossibility.
9. If the stage needs user input under the decision policy, write both outputs with `status: NEEDS_USER`.
10. If the stage fails, write both outputs with `status: FAIL` and a concrete blocking reason.
11. If `feature_name_locked: true`, keep the existing `feature_name` exactly as provided by the harness. Do not rename or invent a different feature slug.
12. End with a concise summary; the harness will inspect files, not your final message.

## Machine Result JSON Contract
The harness reads `.ai/features/start-batchfile/00_spec.result.json` first. Keep the `## 단계 결과` section in `.ai/features/start-batchfile/00_spec.md` for humans, but write this JSON file for the harness.

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
- none

## Additional Stage Inputs
- none

## Retry Context
- none

## Current Git Hints
- current_head: 1251eb84b69737a39554b0ed75c5e36f08004a8c
- changed_paths_excluding_runs: []
- latest_harness_verification: none

---

---
stage: "00_specify"
role: "fast_specification_and_plan"
preferred_model: "Antigravity"
model_policy: "preferred_not_hard_block"
required_inputs:
  - "user_request"
optional_inputs:
  - "existing_codebase"
outputs:
  - ".ai/features/start-batchfile/00_spec.md"
allowed_writes:
  - ".ai/features/start-batchfile/00_spec.md"
forbidden_writes:
  - "production_code"
  - "tests"
human_gate_required: "defer_to_output"
default_next_stage: "01_develop"
---

# Fast Specify 프리셋 (0단계)

## 경로 원칙

- 프로덕션 코드는 루트 `src/` 하위 파일만 의미한다.
- 테스트 코드는 루트 `tests/` 하위 파일만 의미한다.
- 새 테스트 파일은 `tests/` 하위에만 만든다. `src/` 하위에 테스트 파일을 만들지 않는다.
- `requirements.txt`, `run.ps1`, 설정 파일, 의존성 파일, 실행 스크립트 같은 보조 파일도 루트에 만들지 않는다. 필요하면 반드시 `src/` 또는 `tests/` 하위에 둔다.
- `vendor/`, `packages/`, `dist/`, `build/` 등 외부/생성 산출물 디렉터리는 계획/수정/검증 대상에서 제외하고, 필요하면 생성물 또는 외부 산출물로만 기록한다.

## 실행 정책

- 권장 담당 모델은 Antigravity이다.
- 다른 모델이 이 단계를 실행하더라도 중지하지 않는다.
- 담당 모델이 권장 모델과 다르면 `00_spec.md`의 `## 단계 결과`에 `model_mismatch: true`와 실제 실행 모델을 기록한다.
- 이 단계는 기존 full 파이프라인의 `00_specify`와 `01_plan`을 합친 빠른 작업 정의 단계이다.
- 코드를 작성하거나 수정하지 않는다.
- high risk 작업은 fast 파이프라인으로 진행하지 말고 `status: NEEDS_USER`로 멈추며 full 파이프라인 사용을 권고한다.

---

## 역할

너는 이 프로젝트의 fast 파이프라인 기획 담당이다.
사용자 요청을 바로 구현 가능한 짧은 작업 카드로 정리하고, 구현자가 따라갈 최소 계획과 검증 기준을 남긴다.

---

## 작업 순서

1. 사용자 요청의 목표와 범위를 파악한다.
2. 기존 코드베이스를 확인해 관련 파일, 기존 패턴, 영향 범위를 파악한다.
3. 모호한 점이 fast 진행을 막을 정도이면 `status: NEEDS_USER`로 멈춘다.
4. 보안, 인증/인가, 결제, 데이터 마이그레이션, 공개 API 계약 변경, 대규모 리팩터링, 되돌리기 어려운 변경은 `risk_level: high`로 보고 full 파이프라인을 권고한다.
5. low/medium risk면 구현 가능한 acceptance criteria와 간단한 파일 단위 계획을 작성한다.
6. `.ai/features/start-batchfile/00_spec.md`에 결과를 기록한다.

---

## 판단 기준

- `low`: 문구 수정, 작은 UI 조정, 단일 함수/컴포넌트 수정, 명확한 버그 수정
- `medium`: 일반 기능 추가, 여러 파일 변경, 테스트 추가가 필요한 변경
- `high`: 인증/인가, 결제, 보안, 데이터 삭제/변환/마이그레이션, 공개 API 계약 변경, 대규모 구조 변경

fast 파이프라인은 `low`와 `medium`을 기본 대상으로 한다.

---

## 사용자 판단 요청 형식

질문이 필요하면 `.ai/features/start-batchfile/00_spec.md`에 아래 형식만 작성하고 멈춘다.

```markdown
# 00_spec - start-batchfile

작성: [실제 실행 모델]
일시: YYYY-MM-DD

## 사용자 판단 요청
- status: NEEDS_USER
- 질문:
- 추천안:
- 대안:
- 사용자가 답하면 재개할 단계: 00_specify

## 단계 결과
- status: NEEDS_USER
- next_stage: 00_specify
- human_gate_required: true
- blocking_reason:
- risk_level:
- produced_files:
  - .ai/features/start-batchfile/00_spec.md
- changed_files:
- commit_created: false
- commit_message:
- model_mismatch: false
- actual_model:
```

---

## 기록 양식

```markdown
# 00_spec - start-batchfile

작성: [실제 실행 모델]
일시: YYYY-MM-DD

## 목표
- 이번 변경이 달성해야 하는 결과를 한두 줄로 요약

## 기능명
- feature_name: [기능명 slug]
- naming_reason:

## Acceptance Criteria
- 검증 가능한 완료 조건 3~7개

## 제외 범위
- 이번 fast 변경에서 하지 않는 것

## 기존 코드 영향
- 관련 파일:
- 재사용할 기존 모듈/패턴:
- 충돌 가능성이 있는 부분:

## 구현 계획
- src/path/to/file.py: 변경할 내용
- tests/path/to/test_file.py: 추가 또는 수정할 테스트

## 데이터 / 제어 흐름
- 입력이 어디서 들어와 어떤 단계를 거쳐 출력되는지 간단히 설명

## 검증 계획
- 실행할 테스트/빌드 명령:
- 정상 경로:
- 오류/엣지 경로:

## 위험도 및 파이프라인 판단
- risk_level: low / medium / high
- fast_pipeline_allowed: true / false
- full_pipeline_recommended: true / false
- 판단 근거:

## 단계 결과
- status: PASS / NEEDS_USER / FAIL
- next_stage: 01_develop
- human_gate_required: false
- blocking_reason: 없음
- risk_level: low / medium / high
- produced_files:
  - .ai/features/start-batchfile/00_spec.md
- changed_files:
- commit_created: false
- commit_message:
- model_mismatch: false
- actual_model:
```

---

## 금지 사항

- 코드를 작성하거나 수정하지 않는다.
- 테스트 코드를 작성하거나 수정하지 않는다.
- high risk 작업을 fast로 억지 진행하지 않는다.
- 스펙에 없는 기능을 임의로 확장하지 않는다.
