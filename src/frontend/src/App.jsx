import { useCallback, useEffect, useMemo, useState } from 'react';
import DashboardSection from './components/DashboardSection.jsx';
import StatusBanner from './components/StatusBanner.jsx';

const DASHBOARD_ENDPOINT = '/api/v1/market/dashboard';

function getSectionSummary(sections) {
  return sections.reduce(
    (summary, section) => {
      section.items.forEach((item) => {
        summary.total += 1;
        if (item.changePercent === null || item.changePercent === undefined || Number.isNaN(Number(item.changePercent))) {
          summary.neutral += 1;
        } else if (Number(item.changePercent) > 0) {
          summary.up += 1;
        } else if (Number(item.changePercent) < 0) {
          summary.down += 1;
        } else {
          summary.neutral += 1;
        }
      });
      return summary;
    },
    { total: 0, up: 0, down: 0, neutral: 0 },
  );
}

function App() {
  const [dashboard, setDashboard] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');

  const loadDashboard = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage('');

    try {
      const response = await fetch(DASHBOARD_ENDPOINT);
      if (!response.ok) {
        throw new Error(`API 응답 오류 (${response.status})`);
      }
      const data = await response.json();
      setDashboard(data);
    } catch (error) {
      setDashboard(null);
      setErrorMessage(error instanceof Error ? error.message : '대시보드 데이터를 불러오지 못했습니다.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  const sections = dashboard?.sections ?? [];
  const summary = useMemo(() => getSectionSummary(sections), [sections]);
  const generatedAt = dashboard?.generatedAt ? new Date(dashboard.generatedAt).toLocaleString('ko-KR') : '-';

  return (
    <main className="appShell">
      <header className="dashboardHeader">
        <div>
          <p className="eyebrow">Global Market Overview</p>
          <h1>주식 대시보드</h1>
          <p className="headerMeta">미국/한국/기타국 대표지수와 주요 환율을 한 화면에서 확인합니다.</p>
        </div>
        <button className="refreshButton" type="button" onClick={loadDashboard} disabled={isLoading}>
          {isLoading ? '갱신 중' : '새로고침'}
        </button>
      </header>

      <section className="summaryStrip" aria-label="대시보드 요약">
        <div>
          <span>전체 항목</span>
          <strong>{summary.total}</strong>
        </div>
        <div>
          <span>상승</span>
          <strong className="positiveText">{summary.up}</strong>
        </div>
        <div>
          <span>하락</span>
          <strong className="negativeText">{summary.down}</strong>
        </div>
        <div>
          <span>보합/기타</span>
          <strong className="neutralText">{summary.neutral}</strong>
        </div>
        <div>
          <span>기준 시각</span>
          <strong>{generatedAt}</strong>
        </div>
      </section>

      <StatusBanner
        isLoading={isLoading}
        errorMessage={errorMessage}
        isEmpty={!isLoading && !errorMessage && sections.length === 0}
        onRetry={loadDashboard}
      />

      <section className="dashboardGrid" aria-label="시장 데이터 섹션">
        {isLoading
          ? Array.from({ length: 4 }).map((_, index) => <DashboardSection key={index} isLoading />)
          : sections.map((section) => <DashboardSection key={section.id} section={section} />)}
      </section>
    </main>
  );
}

export default App;
