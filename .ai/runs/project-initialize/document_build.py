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


DOCX_PATH = ".ai/docs/project-initialize_명세서.docx"


def build_document():
    doc = create_doc()

    # 1. 개요
    add_h1(doc, "1. 개요")
    add_table(
        doc,
        headers=["항목", "내용"],
        rows=[
            ["기능 이름", "주식 시장 대시보드 초기 구성"],
            ["기능 목적", "React 화면과 FastAPI 백엔드로 주요 지수와 환율을 한 화면에서 조회하는 초기 웹 대시보드 구성"],
            ["최종 판정", "PASS"],
            ["최종 완성 일시", "2026-05-28"],
        ],
    )
    add_paragraph(
        doc,
        "사용자는 첫 화면에서 미국 대표지수, 한국 대표지수, 기타국 대표지수, 환율을 구역별로 확인하고 수동 새로고침할 수 있다. "
        "초기 데이터는 자격 증명이 필요 없는 목 어댑터에서 제공하며, 실제 제공자 연동은 어댑터 교체로 확장하도록 분리했다.",
    )

    # 2. 사용 방법
    add_h1(doc, "2. 사용 방법")
    add_h2(doc, "API / 인터페이스")
    add_table(
        doc,
        headers=["구분", "값", "설명"],
        rows=[
            ["헬스 체크", "GET /api/v1/health", "서버 상태를 확인하며 {status: ok} 형태의 JSON을 반환한다."],
            ["대시보드 집계", "GET /api/v1/market/dashboard", "기본 지수와 환율 섹션을 한 번에 반환한다."],
            ["필수 파라미터", "없음", "초기 버전은 고정된 기본 항목 목록을 반환한다."],
            ["성공 응답", "generatedAt, sections, items", "섹션별 항목에는 name, symbol, value, change, changePercent, currency, marketStatus, asOf, source가 포함된다."],
            ["실패 응답", "HTTP 500 + detail", "어댑터 예외 발생 시 안전한 오류 메시지를 반환한다."],
        ],
    )
    add_h2(doc, "호출 예시")
    add_code_block(
        doc,
        "import requests\n\n"
        "response = requests.get(\"http://127.0.0.1:8000/api/v1/market/dashboard\", timeout=10)\n"
        "response.raise_for_status()\n"
        "payload = response.json()\n"
        "for section in payload[\"sections\"]:\n"
        "    print(section[\"title\"], len(section[\"items\"]))",
    )
    add_h2(doc, "입력 / 출력 예시")
    add_code_block(
        doc,
        "GET /api/v1/market/dashboard\n\n"
        "{\n"
        "  \"generatedAt\": \"2026-05-28T06:56:41Z\",\n"
        "  \"sections\": [\n"
        "    {\n"
        "      \"id\": \"us-indexes\",\n"
        "      \"title\": \"미국 대표지수\",\n"
        "      \"items\": [\n"
        "        {\n"
        "          \"name\": \"S&P 500\",\n"
        "          \"symbol\": \"SPX\",\n"
        "          \"value\": 5321.41,\n"
        "          \"change\": 22.19,\n"
        "          \"changePercent\": 0.42,\n"
        "          \"currency\": \"USD\",\n"
        "          \"marketStatus\": \"delayed\",\n"
        "          \"asOf\": \"2026-05-28T06:56:41Z\",\n"
        "          \"source\": \"mock-adapter\"\n"
        "        }\n"
        "      ]\n"
        "    }\n"
        "  ]\n"
        "}",
    )

    # 3. 관련 파일
    add_h1(doc, "3. 관련 파일")
    add_table(
        doc,
        headers=["파일 경로", "역할"],
        rows=[
            ["src/backend/main.py", "FastAPI 앱, CORS, 헬스 체크와 시장 대시보드 API 라우팅"],
            ["src/backend/app/config.py", "백엔드 설정과 CORS 허용 출처 관리"],
            ["src/backend/app/adapters/base.py", "시장 데이터 제공자 교체를 위한 추상 어댑터 인터페이스"],
            ["src/backend/app/adapters/mock_adapter.py", "미국, 한국, 기타국 지수와 환율 목 데이터 생성"],
            ["src/backend/app/schemas/market.py", "대시보드 응답 스키마와 NaN/Infinity 정규화"],
            ["src/backend/requirements.txt", "FastAPI 백엔드 실행 의존성"],
            ["src/frontend/package.json", "React/Vite 프론트엔드 의존성과 실행 스크립트"],
            ["src/frontend/vite.config.js", "Vite 설정과 백엔드 API 프록시"],
            ["src/frontend/src/App.jsx", "대시보드 데이터 fetch, 새로고침, 섹션 요약 집계"],
            ["src/frontend/src/components/DashboardSection.jsx", "각 시장 섹션 렌더링"],
            ["src/frontend/src/components/MarketItemCard.jsx", "개별 지수/환율 카드와 등락 표시"],
            ["src/frontend/src/components/StatusBanner.jsx", "로딩, 오류, 빈 데이터 상태 표시"],
            ["src/frontend/src/index.css", "다크 테마, 카드, 중립/상승/하락 스타일"],
            ["tests/backend/conftest.py", "백엔드 테스트 import 경로 설정"],
            ["tests/backend/test_adapters.py", "목 어댑터의 섹션 및 항목 구성 검증"],
            ["tests/backend/test_api.py", "API 정상 응답과 어댑터 실패 응답 검증"],
            ["tests/backend/test_schemas.py", "수치 정규화와 스키마 검증"],
        ],
    )

    # 4. 주요 설계 결정
    add_h1(doc, "4. 주요 설계 결정")
    add_h2(doc, "구현 접근 방식")
    add_paragraph(
        doc,
        "프로덕션 코드는 프로젝트 계약에 맞춰 src/backend와 src/frontend로 분리했다. "
        "백엔드는 FastAPI 라우터와 Pydantic 스키마를 중심으로 구성하고, 프론트엔드는 React/Vite 단일 화면에서 4개 시장 섹션을 렌더링한다.",
    )
    add_paragraph(
        doc,
        "외부 데이터 제공자는 MarketDataAdapter 인터페이스 뒤로 숨겼다. 현재 구현은 MockMarketDataAdapter를 기본값으로 사용하므로 API 키 없이 동작하며, 향후 실제 시세 제공자 연동 시 어댑터 구현만 교체할 수 있다.",
    )
    add_h2(doc, "검토한 대안")
    add_bullet(doc, "루트에 package.json 또는 pyproject.toml을 두는 방식은 실행 편의성이 있지만, 보조 파일을 루트에 만들지 말라는 계약을 위반하므로 채택하지 않았다.")
    add_bullet(doc, "실시간 스트리밍 시세는 초기 범위를 넘어 외부 제공자와 장애 처리 복잡도가 커지므로 HTTP 조회와 수동 새로고침을 우선했다.")
    add_bullet(doc, "실제 유료 API 연동은 자격 증명이 제공되지 않았고 초기 대시보드 골격 검증이 목적이므로 보류했다.")
    add_h2(doc, "위험 구간과 완화")
    add_bullet(doc, "NaN 또는 Infinity가 JSON에 섞이는 위험은 Pydantic validator에서 None으로 정규화해 완화했다.")
    add_bullet(doc, "외부 제공자 장애 가능성은 라우터 try-except와 안전한 HTTP 500 JSON 응답 테스트로 방어했다.")
    add_bullet(doc, "기본 포트 충돌 가능성은 Vite 프록시 대상 환경변수와 대체 포트 검증 기록으로 관리했다.")
    add_h2(doc, "리뷰 핵심 포인트와 최종 결정")
    add_bullet(doc, "보합 또는 결측 changePercent가 상승 UI로 표시되는 문제는 중립 tone과 보합/기타 집계로 수정했다.")
    add_bullet(doc, "등락값 양수에는 + 기호를 붙여 등락률 표시와 일관성을 맞췄다.")
    add_bullet(doc, "불필요한 프론트엔드 삼항 조건식은 단순한 소수점 옵션으로 정리했다.")
    add_h2(doc, "거부 / 보류 항목")
    add_bullet(doc, "Python 함수명을 snake_case로 변경하자는 NIT는 이번 범위에서 수용하지 않았다. 프로젝트 계약의 기본 네이밍이 camelCase이고 API 스키마 필드도 camelCase이기 때문이다.")
    add_bullet(doc, "보류 항목과 사용자 판단 요청 항목은 없었다.")

    # 5. 의존성
    add_h1(doc, "5. 의존성")
    add_table(
        doc,
        headers=["라이브러리", "영역", "용도"],
        rows=[
            ["fastapi", "백엔드", "API 서버와 라우팅 구현"],
            ["uvicorn[standard]", "백엔드", "FastAPI 로컬 실행 서버"],
            ["pydantic", "백엔드", "응답 스키마 검증과 안전한 수치 정규화"],
            ["react", "프론트엔드", "대시보드 컴포넌트 구성"],
            ["react-dom", "프론트엔드", "React 앱 브라우저 렌더링"],
            ["vite", "프론트엔드", "개발 서버, 프록시, production build"],
            ["@vitejs/plugin-react", "프론트엔드", "Vite React 변환 플러그인"],
        ],
    )

    # 6. 테스트 현황
    add_h1(doc, "6. 테스트 현황")
    add_table(
        doc,
        headers=["테스트 파일 / 명령", "커버 범위", "최종 결과"],
        rows=[
            ["tests/backend/test_adapters.py", "목 어댑터가 4개 섹션과 필수 시장 항목을 반환하는지 검증", "PASS"],
            ["tests/backend/test_api.py", "헬스 체크, 대시보드 정상 응답, 어댑터 실패 시 안전한 500 응답 검증", "PASS"],
            ["tests/backend/test_schemas.py", "NaN/Infinity 값이 None으로 정규화되는지 검증", "PASS"],
            ["python -m pytest tests/backend", "백엔드 단위/통합 테스트 전체 실행", "7 passed"],
            ["npm.cmd run build (src/frontend)", "React/Vite production build 검증", "PASS"],
            ["하네스 검증", "Python compile, git diff --check, 백엔드 테스트, 프론트엔드 빌드", "PASS"],
        ],
    )
    add_h2(doc, "검증 시 추가된 테스트")
    add_bullet(doc, "어댑터 실패 시 대시보드 API가 내부 예외를 노출하지 않고 안전한 JSON 오류 응답을 반환하는 테스트를 추가했다.")
    add_bullet(doc, "최종 하네스 검증에서는 백엔드 테스트 7개 통과와 프론트엔드 빌드 통과가 확인됐다.")

    # 7. 알려진 한계 및 추후 개선
    add_h1(doc, "7. 알려진 한계 및 추후 개선")
    add_bullet(doc, "현재 시장 데이터는 실제 시세가 아니라 목 데이터다. 실제 제공자 연동 시 MarketDataAdapter 구현을 추가해야 한다.")
    add_bullet(doc, "사용자 인증, 포트폴리오, 관심종목 저장, 알림, 차트 드릴다운, 뉴스, 주문 기능은 초기 범위에서 제외됐다.")
    add_bullet(doc, "실시간 스트리밍은 지원하지 않는다. 초기 버전은 HTTP 조회와 수동 새로고침 중심이다.")
    add_bullet(doc, "인앱 브라우저 스크린샷 기반 UI 검증은 이전 개발 단계에서 수행하지 못했고, 최종 검증은 빌드와 API 테스트 중심으로 완료됐다.")
    add_bullet(doc, "향후 실제 데이터 제공자를 붙일 때는 장애율, 응답 지연, 호출 한도, 캐싱, 기준 시각 신뢰도를 별도 설계해야 한다.")

    os.makedirs(".ai/docs", exist_ok=True)
    doc.save(DOCX_PATH)
    return DOCX_PATH


if __name__ == "__main__":
    path = build_document()
    print(f"생성 완료: {path}")
