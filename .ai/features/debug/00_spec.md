# 00_spec - debug

작성: Codex
일시: 2026-05-28

## 기능 목표
- 대시보드가 정적 mock 수치가 아니라 실행 시점 기준으로 제공자가 반환한 최신 시장 지수/환율 데이터를 표시하도록 한다.
- `generatedAt`만 최신이고 실제 값은 오래된 상태를 방지하며, 데이터 기준 시각과 제공자 상태를 응답에 명확히 반영한다.

## 기능명
- feature_name: debug
- naming_reason: 하네스에서 `feature_name_locked: true`로 `debug`가 고정되어 있어 기존 feature slug를 유지한다.

## 구체적 요구사항
- `/api/v1/market/dashboard`는 현재 `MockMarketDataAdapter`의 고정 샘플 값을 기본 데이터로 반환하지 않아야 한다.
- 미국 지수, 한국 지수, 글로벌 지수, 환율 섹션의 기존 응답 구조와 섹션 id는 유지한다.
- 각 항목의 `value`, `change`, `changePercent`, `currency`, `marketStatus`, `asOf`, `source`는 실제 데이터 제공자 응답을 기준으로 채워야 한다.
- `generatedAt`은 서버가 응답을 생성한 UTC 시각이고, 각 항목의 `asOf`는 제공자가 알려준 해당 값의 기준 시각이어야 한다.
- 제공자별 기준 시각이 없으면 조회 완료 시각을 `asOf`로 사용하되, `marketStatus` 또는 `source`에서 지연/추정 상태가 드러나야 한다.
- 시장 휴장, 장 종료, 시간대 차이로 인해 2026-05-28 당일 체결 값이 없을 수 있는 경우에는 임의로 날짜를 맞추지 않고 제공자의 최신 가능 값을 그대로 사용한다.
- 오래된 fallback/mock 데이터가 최신 데이터처럼 보이면 안 된다. fallback을 쓰는 경우 `marketStatus: unavailable` 또는 명확한 별도 상태와 `source`로 구분해야 한다.
- 외부 제공자 전체 장애로 대시보드 데이터를 신뢰할 수 없으면 기존 API 경계 정책에 맞춰 내부 예외를 노출하지 않는 안전한 JSON 오류 응답을 반환해야 한다.
- 수치 응답에는 `NaN`, `Infinity`, 문자열 percent 중복 변환 문제가 없어야 하며, 기존 `changePercent`는 비율이 아닌 백분율 단위로 유지한다.
- 데이터 제공자 장애, 비정상 수치, 일부 심볼 누락, 네트워크 타임아웃에 대한 테스트를 포함한다.

## 이번 범위에서 제외하는 것
- 유료 실시간 시세, 인증이 필요한 브로커/거래소 API 연동은 제외한다. 현재 요청은 최신 데이터 반영 문제 해결이며, 비밀키나 결제 설정은 제공되지 않았다.
- 과거 차트, 캔들 데이터, 검색/종목 추가 UI는 제외한다. 기존 대시보드 카드 데이터 갱신이 이번 범위다.
- 사용자별 포트폴리오, 주문, 알림 기능은 제외한다. 시장 데이터 조회와 무관하다.
- 영구 저장소 기반 캐시 또는 데이터베이스 마이그레이션은 제외한다. 필요 시 메모리 수준의 짧은 캐시는 다음 단계에서 구현 세부로 검토한다.
- 깨진 한글 문구 복구는 최신 데이터 문제와 직접 관련된 범위가 아니므로 이번 변경의 필수 요구사항에서는 제외한다. 단, 변경 파일 주변의 사용자 노출 문구가 테스트나 구현을 방해하면 최소 수정 대상으로 기록할 수 있다.

## 입력과 출력
- 입력 형태: `GET /api/v1/market/dashboard` 요청. 현재 API는 별도 쿼리 파라미터를 받지 않으므로 입력 파라미터는 추가하지 않는다.
- 출력 형태: 기존 `DashboardResponse` 스키마를 유지한다.
  - `generatedAt: datetime`
  - `sections: DashboardSection[]`
  - `items: MarketItem[]`
- 각 `MarketItem`의 수치 필드는 유한한 숫자 또는 `null`이어야 한다.
- `changePercent`는 `0.42`가 `0.42%`를 의미하는 백분율 값이며, `0.0042` 같은 비율 값으로 중복 변환하지 않는다.
- 비정상 입력 처리: 이번 엔드포인트는 사용자 입력이 없으므로 별도 입력 오류는 없다.
- 외부 의존성 실패 처리:
  - 전체 데이터 생성 실패: HTTP 500과 안전한 JSON 오류 메시지를 반환한다.
  - 일부 항목 실패: 기존 응답 구조를 유지할 수 있으면 해당 항목의 수치를 `null`로 정규화하고 상태/source에서 실패를 드러낸다.

## 기존 코드 영향
- 수정 예상 파일:
  - `src/backend/main.py`: 기본 어댑터를 mock에서 최신 데이터 어댑터로 교체하거나 설정 기반으로 선택한다.
  - `src/backend/app/adapters/base.py`: 필요 시 제공자 오류/부분 실패 표현을 위한 인터페이스를 보강한다.
  - `src/backend/app/adapters/mock_adapter.py`: 테스트/개발 fallback 용도로만 남기고 기본 운영 경로에서 제외한다.
  - `src/backend/app/adapters/`: 최신 시장 데이터 제공자 어댑터를 추가한다.
  - `src/backend/app/config.py`: 제공자 URL, 타임아웃, 짧은 캐시 TTL 같은 설정이 필요하면 추가한다.
  - `src/backend/app/schemas/market.py`: 기존 응답 호환성을 유지하되 상태 값이나 nullable 수치 검증이 부족하면 보강한다.
  - `tests/backend/test_adapters.py`, `tests/backend/test_api.py`, `tests/backend/test_schemas.py`: 최신 데이터 어댑터와 실패 경로 테스트를 추가/갱신한다.
- 사용할 기존 모듈/유틸:
  - `MarketDataAdapter` 추상 인터페이스
  - `DashboardResponse`, `MarketItem` 스키마의 유한 수치 정규화 로직
  - FastAPI의 기존 안전 오류 응답 패턴
- 충돌 가능성:
  - 현재 테스트는 mock 데이터의 고정 항목명과 개수를 기대하므로 최신 데이터 제공자 도입에 맞춰 테스트 의도를 분리해야 한다.
  - 네트워크 호출이 테스트를 불안정하게 만들 수 있으므로 테스트에서는 제공자 호출을 fake/stub로 대체해야 한다.
  - 외부 제공자 심볼 체계가 기존 표시명과 다를 수 있어 내부 심볼 매핑이 필요하다.

## 기술적 제약
- 외부 데이터 제공자는 어댑터 인터페이스 뒤에 두고 비즈니스/API 경계와 분리한다.
- 비밀키가 필요한 제공자는 기본 구현으로 사용하지 않는다. 기본값은 무인증 공개 데이터 소스 또는 표준 라이브러리 기반 호출을 우선한다.
- 새 외부 라이브러리는 꼭 필요할 때만 추가하며, 추가가 필요하면 `src/backend/requirements.txt`에만 반영한다.
- 네트워크 호출에는 타임아웃과 실패 처리를 명시한다.
- API 응답은 기존 프론트엔드가 깨지지 않도록 스키마 호환성을 유지한다.
- 금융 데이터는 제공자 지연, 휴장, 시간대 차이가 있으므로 "최신"은 서버 실행일 문자열이 아니라 제공자가 반환하는 최신 가능 quote 기준으로 정의한다.

## 위험도 및 게이트
- risk_level: high
- human_gate_required: true
- human_gate_reason: 외부 시장 데이터 제공자 연동과 사용자에게 직접 보이는 금융 수치 변경이 포함되며, 새 외부 의존성 가능성이 있어 사람 승인 후 다음 단계로 진행한다.

## 사용자 확인 사항
- 질문 없음.
- 기본 결정:
  - `feature_name`은 하네스 잠금값 `debug`를 유지한다.
  - 인증키 없이 동작 가능한 최신 데이터 경로를 기본으로 한다. 비밀키가 없는 상태에서 유료/인증 API를 요구하면 진행이 막히기 때문이다.
  - 기존 응답 스키마와 섹션 id는 유지한다. 프론트엔드와 테스트의 변경 범위를 줄이고 기존 UI 호환성을 보존하기 위해서다.
  - 시장 휴장/시간대 차이가 있는 경우 제공자의 최신 가능 기준 시각을 신뢰한다. 날짜를 강제로 2026-05-28로 맞추면 데이터 신뢰성이 떨어진다.
  - mock 데이터는 테스트/개발 fallback 용도로만 남기고, 기본 API 경로에서는 최신 데이터처럼 반환하지 않는다.

## 단계 결과
- status: PASS
- next_stage: 01_plan
- human_gate_required: true
- blocking_reason: 없음
- risk_level: high
- produced_files:
  - .ai/features/debug/00_spec.md
  - .ai/features/debug/00_spec.result.json
- changed_files:
  - .ai/features/debug/00_spec.md
  - .ai/features/debug/00_spec.result.json
- commit_created: false
- commit_message:
- model_mismatch: false
- actual_model: Codex
