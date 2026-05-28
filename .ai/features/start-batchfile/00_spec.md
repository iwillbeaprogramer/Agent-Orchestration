# 00_spec - start-batchfile

작성: Antigravity
일시: 2026-05-28

## 목표
- 사용자가 Windows 환경에서 백엔드(FastAPI)와 프론트엔드(React/Vite) 서비스를 동시에 간편하게 구동 및 종료할 수 있도록 `src/` 디렉터리 하위에 `.bat` 형식의 일괄 실행 및 종료 배치 파일을 작성합니다.

## 기능명
- feature_name: start-batchfile
- naming_reason: 하니스에서 부여된 고유 기능 슬러그를 그대로 유지하여 일관성을 확보합니다.

## Acceptance Criteria
- `src/start.bat` 실행 시, 백엔드(`uvicorn main:app --host 127.0.0.1 --port 8000`)와 프론트엔드(`npm run dev` 온 `127.0.0.1:5173`)가 각각 독립된 명령 프롬프트(CMD) 창에서 오류 없이 병렬 구동되어야 합니다.
- `src/stop.bat` 실행 시, 백엔드 포트(8000)와 프론트엔드 포트(5173)를 점유하고 있는 로컬 프로세스(PID)를 정확하게 탐색하여 안전하고 즉각적으로 종료해야 합니다.
- 두 배치 파일은 실행 위치에 종속되지 않도록 `%~dp0` 상대 경로 매크로를 사용하여 절대 경로 기준으로 백엔드 및 프론트엔드 디렉터리를 찾아 동작하도록 작성합니다.

## 제외 범위
- Windows 환경을 타겟으로 한 `.bat` 파일 작성에 집중하며, Linux/macOS용 쉘 스크립트(`.sh`)나 PowerShell 스크립트(`.ps1`) 제작은 이번 범위에서 제외합니다.
- 백엔드와 프론트엔드의 기존 비즈니스 로직, 패키지 의존성 설정 파일 등의 내부 코드는 변경하지 않습니다.

## 기존 코드 영향
- 관련 파일:
  - [src/backend/main.py](file:///D:/test/vibe-coding-toolkit/Agent%20Orchestration/src/backend/main.py) (포트 8000 및 호스트 사양 확인 완료)
  - [src/frontend/package.json](file:///D:/test/vibe-coding-toolkit/Agent%20Orchestration/src/frontend/package.json) (구동 스크립트 `npm run dev` 확인 완료)
  - [src/frontend/vite.config.js](file:///D:/test/vibe-coding-toolkit/Agent%20Orchestration/src/frontend/vite.config.js) (포트 5173 및 백엔드 프록시 매핑 확인 완료)
- 재사용할 기존 모듈/패턴:
  - 프론트엔드의 `npm run dev` 스크립트 및 백엔드의 `uvicorn` 실행 커맨드를 그대로 호출하여 재사용합니다.
- 충돌 가능성이 있는 부분:
  - 이미 로컬 시스템의 8000 포트나 5173 포트가 사용 중인 경우 프로세스 바인딩 에러가 발생할 수 있습니다. 이를 예방하기 위해 `stop.bat`을 사전에 구동하도록 유도합니다.

## 구현 계획
- `src/start.bat`:
  - CMD 환경에서 `%~dp0` 기준으로 `backend` 디렉터리로 이동 후 `start "Market Dashboard Backend" uvicorn main:app --host 127.0.0.1 --port 8000` 비동기 실행.
  - 이어서 `frontend` 디렉터리로 이동 후 `start "Market Dashboard Frontend" npm run dev` 비동기 실행.
- `src/stop.bat`:
  - `netstat -aon` 조회를 통해 로컬 포트 8000과 5173을 사용하는 프로세스의 PID를 추출합니다.
  - 조회된 PID에 대해 `taskkill /f /pid <PID>`를 순차적으로 실행하여 잔존 프로세스를 깔끔히 청소합니다.

## 데이터 / 제어 흐름
- **시작 흐름**: `start.bat` 실행 -> 백엔드 디렉터리 이동 -> 백엔드 CMD 인스턴스 론칭(8000 포트) -> 프론트엔드 디렉터리 이동 -> 프론트엔드 CMD 인스턴스 론칭(5173 포트) -> 로컬 웹앱 사용 가능.
- **종료 흐름**: `stop.bat` 실행 -> 포트 8000, 5173 사용 PID 탐색 -> 해당 PID 강제 종료 -> 백엔드 및 프론트엔드 CMD 인스턴스 종료 및 포트 반환.

## 검증 계획
- 실행할 테스트/빌드 명령:
  - 수동 구동 테스트: `src/start.bat`을 실행하고 브라우저에서 `http://127.0.0.1:5173`로 접속하여 정상 구동을 확인합니다.
  - 수동 종료 테스트: `src/stop.bat`을 실행한 후 명령 프롬프트에서 `netstat -ano | findstr "8000 5173"`을 실행하여 포트 점유가 깨끗하게 릴리스되었는지 확인합니다.
- 정상 경로:
  - `start.bat` 실행 시 에러 없이 백엔드 및 프론트엔드 서버가 시작되고, `stop.bat` 실행 시 모든 프로세스가 올바르게 리프레시됩니다.
- 오류/엣지 경로:
  - 특정 포트가 닫히지 않고 좀비 프로세스로 남아 있는 경우 `stop.bat`을 한 번 더 작동시켜 안정적으로 킬(kill)할 수 있는지 확인합니다.

## 위험도 및 파이프라인 판단
- risk_level: low
- fast_pipeline_allowed: true
- full_pipeline_recommended: false
- 판단 근거:
  - 비즈니스 도메인 로직이나 데이터베이스 스키마, 결제 및 보안 관련 기능을 일절 수정하지 않으며, 단지 로컬 개발 생산성을 높이기 위한 유틸리티 성격의 단순 스크립트 작성에 국한되므로 위험 수준은 `low`입니다. 따라서 `fast` 파이프라인 진행에 매우 안전하고 적합합니다.

## 단계 결과
- status: PASS
- next_stage: 01_develop
- human_gate_required: false
- blocking_reason: 없음
- risk_level: low
- produced_files:
  - .ai/features/start-batchfile/00_spec.md
- changed_files: []
- commit_created: false
- commit_message: ""
- model_mismatch: false
- actual_model: Antigravity
