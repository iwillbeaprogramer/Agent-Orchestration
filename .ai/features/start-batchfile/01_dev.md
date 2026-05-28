# 01_dev - start-batchfile

작성: Codex
일시: 2026-05-28

## 구현 요약
- `src/start.bat`를 추가해 `%~dp0` 기준으로 `src/backend`, `src/frontend`를 찾고 각각 별도 CMD 창에서 backend와 frontend를 시작하도록 구현했습니다.
- `src/stop.bat`를 추가해 8000, 5173 포트의 LISTENING PID를 `netstat`/`findstr`로 찾아 `taskkill /f /pid`로 종료하도록 구현했습니다.
- 배치 파일 계약을 확인하는 pytest 테스트를 `tests/test_batch_scripts.py`에 추가했습니다.

## 처리한 verify 실패
- 이전 02_verify.md 실패 항목: 없음
- 하네스 검증 JSON 실패 항목: 없음
- 반영 내용: 신규 구현

## 변경 파일
- `src/start.bat`: backend `uvicorn main:app --host 127.0.0.1 --port 8000`, frontend `npm run dev`를 각각 별도 CMD 창에서 실행
- `src/stop.bat`: 8000/5173 포트 점유 PID 검색 및 강제 종료
- `tests/test_batch_scripts.py`: 배치 파일 위치, `%~dp0` 사용, 실행/종료 명령 계약 검증

## 계획과 달라진 점
- 없음

## 테스트
- 실행한 테스트 명령: `pytest`
- 결과: 9 passed
- 추가/수정한 테스트: `tests/test_batch_scripts.py`
- 참고: `cmd /d /c "netstat -aon | findstr /r /c:"":8000 .*LISTENING""""`로 CMD `findstr` 패턴 동작을 확인했습니다. 현재 8000/5173 포트가 이미 다른 실행 세션에서 사용 중이라, 이 단계에서는 `stop.bat`를 실제 실행해 프로세스를 종료하지 않았습니다.

## 남은 위험
- verify 단계에서 Windows CMD로 `src/start.bat` 실행 후 `http://127.0.0.1:5173` 접속과 `src/stop.bat` 종료 동작을 실제로 확인해야 합니다.
- `stop.bat`는 스펙대로 포트 기준으로 종료하므로, 8000 또는 5173을 다른 로컬 프로세스가 점유 중이면 해당 프로세스를 종료합니다.

## Git 정보
- develop_base_commit: 1251eb84b69737a39554b0ed75c5e36f08004a8c
- harness_commit_required: true
- commit_created_by_model: false
- commit_mode_suggestion: create
- commit_message_suggestion: start-batchfile[20260528-161012][01_develop]
- pre_commit_diff_command: git diff 1251eb84b69737a39554b0ed75c5e36f08004a8c
- changed_files:
  - `src/start.bat`
  - `src/stop.bat`
  - `tests/test_batch_scripts.py`
  - `.ai/features/start-batchfile/01_dev.md`
  - `.ai/features/start-batchfile/01_dev.result.json`
- harness_commit_blocking_reason: 없음

## 단계 결과
- status: PASS
- next_stage: 02_verify
- human_gate_required: false
- blocking_reason: 없음
- risk_level: low
- produced_files:
  - `.ai/features/start-batchfile/01_dev.md`
  - `.ai/features/start-batchfile/01_dev.result.json`
- changed_files:
  - `src/start.bat`
  - `src/stop.bat`
  - `tests/test_batch_scripts.py`
  - `.ai/features/start-batchfile/01_dev.md`
  - `.ai/features/start-batchfile/01_dev.result.json`
- harness_commit_required: true
- commit_created_by_model: false
- commit_mode_suggestion: create
- commit_message_suggestion: start-batchfile[20260528-161012][01_develop]
- test_commands:
  - `pytest`
- model_mismatch: true
- actual_model: Codex
