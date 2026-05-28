function formatNumber(value, currency) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return '-';
  }

  return new Intl.NumberFormat('ko-KR', {
    maximumFractionDigits: currency === 'KRW' ? 2 : 2,
    minimumFractionDigits: 2,
  }).format(value);
}

function formatChange(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return '-';
  }

  const sign = value > 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
}

function MarketItemCard({ item }) {
  const changePercent = item.changePercent ?? 0;
  const tone = changePercent >= 0 ? 'positive' : 'negative';
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
        <span>{formatNumber(item.change, item.currency)}</span>
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
