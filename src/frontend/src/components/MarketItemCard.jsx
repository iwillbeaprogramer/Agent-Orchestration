function formatNumber(value, currency) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return '-';
  }

  return new Intl.NumberFormat('ko-KR', {
    maximumFractionDigits: 2,
    minimumFractionDigits: 2,
  }).format(value);
}

function formatSignedNumber(value, currency) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return '-';
  }

  const numericValue = Number(value);
  const sign = numericValue > 0 ? '+' : '';
  return `${sign}${formatNumber(numericValue, currency)}`;
}

function formatChange(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return '-';
  }

  const numericValue = Number(value);
  const sign = numericValue > 0 ? '+' : '';
  return `${sign}${numericValue.toFixed(2)}%`;
}

function getMarketTone(changePercent) {
  if (changePercent === null || changePercent === undefined || Number.isNaN(Number(changePercent))) {
    return 'neutral';
  }

  const numericChangePercent = Number(changePercent);
  if (numericChangePercent > 0) {
    return 'positive';
  }
  if (numericChangePercent < 0) {
    return 'negative';
  }
  return 'neutral';
}

function MarketItemCard({ item }) {
  const tone = getMarketTone(item.changePercent);
  const asOf = item.asOf ? new Date(item.asOf).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }) : '-';

  return (
    <div className={`marketCard ${tone}`}>
      <div className="itemTopLine">
        <div>
          <strong>{item.name}</strong>
          <span>{item.symbol}</span>
        </div>
        <span className="statusPill">{item.marketStatus}</span>
      </div>
      <div className="itemValueLine">
        <span className="itemValue">{formatNumber(item.value, item.currency)}</span>
        <span className="currencyLabel">{item.currency}</span>
      </div>
      <div className="itemChangeLine">
        <span>{formatSignedNumber(item.change, item.currency)}</span>
        <strong>{formatChange(item.changePercent)}</strong>
      </div>
      <div className="itemFooter">
        <span>{asOf}</span>
        <span>{item.source}</span>
      </div>
    </div>
  );
}

export default MarketItemCard;
