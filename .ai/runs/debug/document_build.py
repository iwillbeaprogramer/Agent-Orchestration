import os
import sys

sys.path.insert(0, ".ai/templates")

from docx_helper import (
    add_bullet,
    add_code_block,
    add_h1,
    add_h2,
    add_paragraph,
    add_table,
    create_doc,
)


DOCX_PATH = ".ai/docs/debug_명세서.docx"


def build_document():
    doc = create_doc()

    add_h1(doc, "1. 개요")
    add_table(
        doc,
        headers=["항목", "내용"],
        rows=[
            ["기능 이름", "대시보드 최신 시장 데이터 반영"],
            [
                "기능 목적",
                "/api/v1/market/dashboard가 고정 mock 값 대신 Yahoo Finance v8 Chart API의 최신 가능 시장 지수와 환율 값을 반환하도록 한다.",
            ],
            ["최종 판정", "PASS"],
            ["최종 완성 일시", "2026-05-28"],
        ],
    )
    add_paragraph(
        doc,
        "이 기능은 응답 스키마와 섹션 id를 유지하면서, generatedAt만 최신이고 실제 수치가 오래된 상태를 방지하기 위해 기본 시장 데이터 제공자를 Yahoo Finance 기반 어댑터로 교체했다.",
    )

    add_h1(doc, "2. 사용 방법")
    add_h2(doc, "API / 인터페이스")
    add_bullet(doc, "엔드포인트: GET /api/v1/market/dashboard")
    add_bullet(doc, "요청 파라미터: 없음")
    add_bullet(doc, "성공 응답: DashboardResponse 모델. generatedAt과 sections 배열을 반환한다.")
    add_bullet(
        doc,
        "각 MarketItem은 name, symbol, value, change, changePercent, currency, marketStatus, asOf, source 필드를 포함한다.",
    )
    add_bullet(
        doc,
        "실패 응답: 전체 제공자 장애로 사용 가능한 시장 값이 없으면 HTTP 500과 안전한 JSON detail을 반환한다.",
    )
    add_h2(doc, "호출 예시")
    add_code_block(
        doc,
        """import requests

response = requests.get("http://localhost:8000/api/v1/market/dashboard", timeout=10)
response.raise_for_status()
payload = response.json()
print(payload["generatedAt"])
print(payload["sections"][0]["items"][0]["source"])""",
    )
    add_h2(doc, "입력 / 출력 예시")
    add_code_block(
        doc,
        """GET /api/v1/market/dashboard

200 OK
{
  "generatedAt": "2026-05-28T00:00:00+00:00",
  "sections": [
    {
      "id": "us-indexes",
      "title": "미국 대표지수",
      "items": [
        {
          "name": "S&P 500",
          "symbol": "SPX",
          "value": 100.0,
          "change": 5.0,
          "changePercent": 5.263157894736842,
          "currency": "USD",
          "marketStatus": "regular",
          "asOf": "2026-05-28T00:00:00+00:00",
          "source": "yahoo-finance-v8"
        }
      ]
    }
  ]
}""",
    )

    add_h1(doc, "3. 관련 파일")
    add_table(
        doc,
        headers=["파일 경로", "역할"],
        rows=[
            ["src/backend/main.py", "대시보드 API 엔드포인트를 제공하고 기본 시장 데이터 어댑터를 YahooMarketDataAdapter로 연결한다."],
            ["src/backend/app/adapters/yahoo_adapter.py", "Yahoo Finance v8 Chart API 호출, 병렬 조회, 캐시, 정규화, 장애 처리를 담당한다."],
            ["src/backend/app/config.py", "Yahoo API 타임아웃과 캐시 TTL 기본 설정을 보관한다."],
            ["src/backend/app/schemas/market.py", "DashboardResponse와 MarketItem 스키마 및 유한 수치 정규화 규칙을 정의한다."],
            ["tests/backend/test_adapters.py", "Yahoo 어댑터의 파싱, 캐시, 부분 실패, malformed 응답, 전체 실패 경로를 검증한다."],
            ["tests/backend/test_api.py", "대시보드 API 성공 응답과 어댑터 장애 시 안전한 500 JSON 응답을 검증한다."],
        ],
    )

    add_h1(doc, "4. 주요 설계 결정")
    add_h2(doc, "구현 접근 방식")
    add_paragraph(
        doc,
        "기본 데이터 제공자를 MockMarketDataAdapter에서 YahooMarketDataAdapter로 교체했다. 새 어댑터는 기존 MarketDataAdapter 인터페이스 뒤에 위치하므로 API 라우터와 응답 스키마는 유지되고, 외부 데이터 제공자 연동은 비즈니스/API 경계와 분리된다.",
    )
    add_bullet(doc, "Yahoo Finance v8 Chart API를 심볼별로 호출하고 ThreadPoolExecutor로 18개 항목을 병렬 조회한다.")
    add_bullet(doc, "60초 인메모리 캐시를 둬 잦은 새로고침으로 인한 제공자 호출과 rate limit 위험을 낮춘다.")
    add_bullet(doc, "HTTP 호출에는 5초 타임아웃과 브라우저 User-Agent를 적용한다.")
    add_bullet(doc, "JPYKRW=X는 기존 UI의 JPY/KRW (100엔) 표기에 맞춰 100을 곱해 노출한다.")
    add_bullet(doc, "changePercent는 비율이 아니라 백분율 값으로 계산해 기존 프론트엔드 호환성을 유지한다.")

    add_h2(doc, "검토했지만 채택하지 않은 대안")
    add_bullet(
        doc,
        "Yahoo Finance v7 Quote API 일괄 조회: 단일 HTTP 호출로 빠르지만 세션 쿠키와 crumb 토큰 요구로 401 차단이 발생해 지속 가능한 기본 경로로 보지 않았다.",
    )
    add_bullet(
        doc,
        "yfinance 라이브러리 추가: API 우회 처리는 편하지만 무거운 의존성과 내부 스크래핑/Pandas 의존성이 있어, 표준 라이브러리 직접 호출로 충분한 이번 범위에서는 제외했다.",
    )

    add_h2(doc, "위험 구간과 완화")
    add_bullet(doc, "Yahoo Finance 공개 엔드포인트는 차단 또는 응답 형식 변경 가능성이 있다. 60초 캐시, User-Agent, 타임아웃, 장애 처리로 영향을 줄였다.")
    add_bullet(doc, "외부 API 지연이 대시보드 응답을 늦출 수 있다. 병렬 조회와 5초 하드 타임아웃으로 순차 지연 누적을 피했다.")
    add_bullet(doc, "일부 심볼 실패는 전체 대시보드 실패로 확대하지 않고 해당 항목을 unavailable과 null 수치로 표시한다.")

    add_h2(doc, "리뷰 핵심 포인트와 최종 결정")
    add_bullet(doc, "03_review에서 BLOCKER, MAJOR, MINOR, NIT 지적은 모두 0건이었다.")
    add_bullet(doc, "리뷰는 v8 Chart API 병렬 호출, 60초 캐시, NaN/Infinity 정규화, JPY/KRW 100엔 보정을 요구사항에 부합하는 구현으로 판정했다.")
    add_bullet(doc, "04_fix에서는 처리할 지적이나 실패 입력이 없어 프로덕션 코드와 테스트 코드를 추가 변경하지 않았다.")

    add_h2(doc, "거부 또는 보류된 항목")
    add_paragraph(doc, "리뷰 지적 사항이 없었으므로 거부하거나 보류한 항목은 없다.")

    add_h1(doc, "5. 의존성")
    add_table(
        doc,
        headers=["라이브러리 / 모듈", "용도"],
        rows=[
            ["urllib.request", "Yahoo Finance v8 Chart API에 HTTP 요청을 보내고 JSON 응답을 수신한다."],
            ["concurrent.futures.ThreadPoolExecutor", "18개 시장 지수와 환율 항목을 병렬 조회한다."],
            ["datetime", "generatedAt과 asOf 시각을 UTC 기준으로 생성하거나 변환한다."],
            ["math", "NaN, Infinity 같은 비유한 수치를 감지하고 null로 정규화한다."],
            ["threading", "인메모리 캐시 접근을 잠금으로 보호한다."],
            ["python-docx", "이 명세서 .docx 산출물을 생성하기 위해 docx_helper가 사용하는 문서 생성 라이브러리다."],
        ],
    )
    add_paragraph(doc, "기능 구현을 위해 새 서드파티 런타임 의존성은 추가하지 않았다.")

    add_h1(doc, "6. 테스트 현황")
    add_table(
        doc,
        headers=["테스트 파일 / 명령", "커버 범위", "결과"],
        rows=[
            [
                "tests/backend/test_adapters.py",
                "Yahoo 응답 파싱, 18개 항목 조회, 캐시 방어 복사, JPY/KRW 스케일링, 부분 실패 unavailable 처리, malformed 응답, 전체 실패 예외",
                "PASS",
            ],
            [
                "tests/backend/test_api.py",
                "GET /api/v1/market/dashboard 성공 응답, 섹션 id 유지, 어댑터 전체 실패 시 안전한 HTTP 500 JSON 응답",
                "PASS",
            ],
            ["python -m pytest", "백엔드 테스트 전체 실행", "PASS"],
            ["npm.cmd run build (cwd: src/frontend)", "프론트엔드 빌드 검증", "PASS"],
            ["git diff --check", "공백 오류와 패치 형식 검증", "PASS"],
        ],
    )
    add_paragraph(doc, "05_verify 기준 기존 테스트는 14개 모두 통과했으며, 02_dev 단계에서 추가한 테스트가 충분해 05_verify 단계에서 새 테스트 파일은 추가하지 않았다.")

    add_h1(doc, "7. 알려진 한계 및 추후 개선")
    add_bullet(doc, "Yahoo Finance 공개 엔드포인트는 인증이 없지만 제공자 정책 변경, 차단, 응답 형식 변경 가능성이 남아 있다.")
    add_bullet(doc, "캐시는 프로세스 메모리 기반이므로 서버 재시작 시 초기화된다.")
    add_bullet(doc, "provider별 장애율, 응답 시간, 마지막 성공 시각 같은 운영 관측 지표는 아직 추가되지 않았다.")
    add_bullet(doc, "유료 실시간 시세, 인증이 필요한 브로커/거래소 API, 과거 차트, 종목 검색 UI, 사용자별 포트폴리오 기능은 이번 범위에서 제외되었다.")

    os.makedirs(".ai/docs", exist_ok=True)
    doc.save(DOCX_PATH)
    return DOCX_PATH


if __name__ == "__main__":
    path = build_document()
    print(f"생성 완료: {path}")
