import { useCallback, useEffect, useMemo, useState } from 'react';
import DashboardSection from './components/DashboardSection.jsx';
import SettingsTab from './components/SettingsTab.jsx';
import StatusBanner from './components/StatusBanner.jsx';
import StockDetailTab from './components/StockDetailTab.jsx';
import TabNavigation from './components/TabNavigation.jsx';

const DASHBOARD_ENDPOINT = '/api/v1/market/dashboard';
const STOCK_TABS_STORAGE_KEY = 'marketDashboard.stockTabs';
const DASHBOARD_TAB_ID = 'dashboard';
const SETTINGS_TAB_ID = 'settings';

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

function loadStoredTabs() {
  try {
    const rawValue = window.localStorage.getItem(STOCK_TABS_STORAGE_KEY);
    if (!rawValue) {
      return [];
    }
    const parsedValue = JSON.parse(rawValue);
    if (!Array.isArray(parsedValue)) {
      return [];
    }
    return parsedValue.filter((item) => item?.providerSymbol && item?.displaySymbol && item?.name);
  } catch {
    return [];
  }
}

function saveStoredTabs(tabs) {
  try {
    window.localStorage.setItem(STOCK_TABS_STORAGE_KEY, JSON.stringify(tabs));
  } catch {
    // localStorage can fail in private browsing or restricted test environments.
  }
}

function App() {
  const [dashboard, setDashboard] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');
  const [stockTabs, setStockTabs] = useState(() => loadStoredTabs());
  const [activeTab, setActiveTab] = useState(DASHBOARD_TAB_ID);

  const loadDashboard = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage('');

    try {
      const response = await fetch(DASHBOARD_ENDPOINT);
      if (!response.ok) {
        throw new Error(`API response error (${response.status})`);
      }
      const data = await response.json();
      setDashboard(data);
    } catch (error) {
      setDashboard(null);
      setErrorMessage(error instanceof Error ? error.message : 'Unable to load market dashboard data.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  useEffect(() => {
    saveStoredTabs(stockTabs);
  }, [stockTabs]);

  const sections = dashboard?.sections ?? [];
  const summary = useMemo(() => getSectionSummary(sections), [sections]);
  const generatedAt = dashboard?.generatedAt ? new Date(dashboard.generatedAt).toLocaleString('ko-KR') : '-';
  const activeStock = stockTabs.find((item) => item.providerSymbol === activeTab);

  const tabs = useMemo(
    () => [
      { id: DASHBOARD_TAB_ID, label: 'Dashboard', type: 'dashboard' },
      ...stockTabs.map((item) => ({ id: item.providerSymbol, label: item.displaySymbol || item.symbol, type: 'stock' })),
      { id: SETTINGS_TAB_ID, label: 'Settings', type: 'settings' },
    ],
    [stockTabs],
  );

  const handleAddStock = useCallback((stock) => {
    setStockTabs((currentTabs) => {
      if (currentTabs.some((item) => item.providerSymbol === stock.providerSymbol)) {
        return currentTabs;
      }
      return [...currentTabs, stock];
    });
    setActiveTab(stock.providerSymbol);
  }, []);

  const handleRemoveStock = useCallback(
    (providerSymbol) => {
      setStockTabs((currentTabs) => currentTabs.filter((item) => item.providerSymbol !== providerSymbol));
      if (activeTab === providerSymbol) {
        setActiveTab(DASHBOARD_TAB_ID);
      }
    },
    [activeTab],
  );

  return (
    <main className="appShell">
      <header className="dashboardHeader">
        <div>
          <p className="eyebrow">Global Market Overview</p>
          <h1>Market Dashboard</h1>
          <p className="headerMeta">Track core indexes, FX rates, and your selected Korea/US stocks or ETFs.</p>
        </div>
        <button className="refreshButton" type="button" onClick={loadDashboard} disabled={isLoading}>
          {isLoading ? 'Refreshing' : 'Refresh'}
        </button>
      </header>

      <TabNavigation tabs={tabs} activeTab={activeTab} onSelectTab={setActiveTab} />

      {activeTab === DASHBOARD_TAB_ID && (
        <>
          <section className="summaryStrip" aria-label="Dashboard summary">
            <div>
              <span>Total items</span>
              <strong>{summary.total}</strong>
            </div>
            <div>
              <span>Up</span>
              <strong className="positiveText">{summary.up}</strong>
            </div>
            <div>
              <span>Down</span>
              <strong className="negativeText">{summary.down}</strong>
            </div>
            <div>
              <span>Flat/Missing</span>
              <strong className="neutralText">{summary.neutral}</strong>
            </div>
            <div>
              <span>Generated</span>
              <strong>{generatedAt}</strong>
            </div>
          </section>

          <StatusBanner
            isLoading={isLoading}
            errorMessage={errorMessage}
            isEmpty={!isLoading && !errorMessage && sections.length === 0}
            onRetry={loadDashboard}
          />

          <section className="dashboardGrid" aria-label="Market data sections">
            {isLoading
              ? Array.from({ length: 4 }).map((_, index) => <DashboardSection key={index} isLoading />)
              : sections.map((section) => <DashboardSection key={section.id} section={section} />)}
          </section>
        </>
      )}

      {activeStock && <StockDetailTab stock={activeStock} onRemoveStock={handleRemoveStock} />}

      {activeTab === SETTINGS_TAB_ID && (
        <SettingsTab
          addedStocks={stockTabs}
          onAddStock={handleAddStock}
          onRemoveStock={handleRemoveStock}
          onOpenStock={setActiveTab}
        />
      )}
    </main>
  );
}

export default App;
