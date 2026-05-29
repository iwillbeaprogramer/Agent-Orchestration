import { useEffect, useState } from 'react';
import StockChart from './StockChart.jsx';

const DETAIL_ENDPOINT = '/api/v1/market/detail';
const RANGES = ['1D', '1M', '3M', '1Y'];

function isFiniteNumber(value) {
  return value !== null && value !== undefined && Number.isFinite(Number(value));
}

function formatNumber(value) {
  if (!isFiniteNumber(value)) {
    return '-';
  }
  return new Intl.NumberFormat('ko-KR', { maximumFractionDigits: 2 }).format(Number(value));
}

function formatPercent(value) {
  if (!isFiniteNumber(value)) {
    return '-';
  }
  const numericValue = Number(value);
  return `${numericValue > 0 ? '+' : ''}${numericValue.toFixed(2)}%`;
}

function getTone(value) {
  if (!isFiniteNumber(value) || Number(value) === 0) {
    return 'neutral';
  }
  return Number(value) > 0 ? 'positive' : 'negative';
}

function StatCard({ label, value, suffix }) {
  return (
    <div className="statCard">
      <span>{label}</span>
      <strong>
        {value}
        {suffix ? <small>{suffix}</small> : null}
      </strong>
    </div>
  );
}

function StockDetailTab({ stock, onRemoveStock }) {
  const [range, setRange] = useState('1M');
  const [detail, setDetail] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    const controller = new AbortController();

    async function loadDetail() {
      setIsLoading(true);
      setErrorMessage('');
      try {
        const params = new URLSearchParams({ symbol: stock.providerSymbol, range });
        const response = await fetch(`${DETAIL_ENDPOINT}?${params.toString()}`, { signal: controller.signal });
        if (!response.ok) {
          throw new Error(`Detail request failed (${response.status})`);
        }
        setDetail(await response.json());
      } catch (error) {
        if (error?.name !== 'AbortError') {
          setDetail(null);
          setErrorMessage(error instanceof Error ? error.message : 'Unable to load stock detail.');
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    }

    loadDetail();
    return () => controller.abort();
  }, [stock.providerSymbol, range]);

  const quote = detail?.quote;
  const instrument = detail?.instrument ?? stock;
  const tone = getTone(quote?.changePercent);

  return (
    <section className="stockDetailLayout" aria-label={`${stock.displaySymbol} detail`}>
      <div className="detailHero">
        <div>
          <p className="eyebrow">
            {instrument.country} · {instrument.exchange} · {instrument.instrumentType?.toUpperCase()}
          </p>
          <h2>{instrument.displaySymbol}</h2>
          <p>{instrument.name}</p>
        </div>
        <div className={`detailPrice ${tone}`}>
          <strong>{formatNumber(quote?.price)}</strong>
          <span>
            {formatNumber(quote?.change)} · {formatPercent(quote?.changePercent)}
          </span>
        </div>
      </div>

      <div className="detailToolbar">
        <div className="rangeGroup" aria-label="Chart range">
          {RANGES.map((item) => (
            <button className={range === item ? 'active' : ''} key={item} type="button" onClick={() => setRange(item)}>
              {item}
            </button>
          ))}
        </div>
        <button className="ghostButton" type="button" onClick={() => onRemoveStock(stock.providerSymbol)}>
          Remove tab
        </button>
      </div>

      {isLoading && <div className="statusBanner neutral">Loading stock detail...</div>}
      {errorMessage && <div className="statusBanner danger">{errorMessage}</div>}

      {detail && (
        <>
          <div className="detailGrid">
            <StatCard label="Open" value={formatNumber(quote.open)} suffix={quote.currency} />
            <StatCard label="High" value={formatNumber(quote.high)} suffix={quote.currency} />
            <StatCard label="Low" value={formatNumber(quote.low)} suffix={quote.currency} />
            <StatCard label="Prev close" value={formatNumber(quote.regularMarketPreviousClose ?? quote.previousClose)} suffix={quote.currency} />
            <StatCard label="Volume" value={formatNumber(quote.volume)} />
            <StatCard label="Market" value={quote.marketStatus || '-'} />
            <StatCard label="As of" value={quote.asOf ? new Date(quote.asOf).toLocaleString('ko-KR') : '-'} />
            <StatCard label="Source" value={quote.source || '-'} />
          </div>
          <StockChart currency={quote.currency} points={detail.chart} />
        </>
      )}
    </section>
  );
}

export default StockDetailTab;
