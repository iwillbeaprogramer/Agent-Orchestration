# 프로젝트 히스토리

로컬 하네스가 자동 생성한 완료 run 인덱스 요약입니다.

- 기록된 feature: 4
- 인덱스: .ai/history/index.json
- PC 후보: .ai/history/pc_candidates.json

## 최근 완료 Run

- 2026-05-29T10:32:18 search (full, complete, verify=PASS)
  - 대시보드-종목탭-설정 탭 구조 요구사항을 확정했다.
  - 설정 탭에서 한국/미국 주식 및 ETF만 검색하고 전용 종목 탭으로 추가하는 범위를 확정했다.
  - 종목 상세 정보와 차트 API/UI의 최소 표시 항목을 정의했다.
- 2026-05-28T16:38:36 debug (full, complete, verify=PASS)
  - 최신 데이터 미반영 문제를 MockMarketDataAdapter 기본 사용과 정적 샘플 수치 문제로 정리했다.
  - 기존 DashboardResponse 스키마와 섹션 id를 유지하면서 실제 제공자 기반 최신 데이터로 교체하는 요구사항을 확정했다.
  - 외부 제공자 장애, 일부 항목 누락, 비유한 수치 정규화, marketStatus/source 명시 요구사항을 기록했다.
- 2026-05-28T16:15:06 start-batchfile (fast, complete, verify=PASS)
  - Added src/start.bat to start backend and frontend from src-relative directories in separate CMD windows.
  - Added src/stop.bat to find LISTENING PIDs on ports 8000 and 5173 and terminate them with taskkill.
  - Added pytest coverage for the batch file contract.
- 2026-05-28T16:04:09 project-initialize (full, complete, verify=PASS)
  - React 프론트엔드와 FastAPI 백엔드 기반 주식/시장 대시보드 초기 스펙을 확정했다.
  - 미국 대표지수, 한국 대표지수, 기타국 대표지수, 환율 섹션의 기본 표시 대상을 정의했다.
  - 외부 데이터 제공자는 어댑터 인터페이스 뒤에 두고 초기 구현은 무자격 증명 공개 데이터 또는 목 데이터로 시작하도록 정했다.
