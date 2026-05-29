import { useMemo, useRef, useState } from 'react';

const WIDTH = 720;
const HEIGHT = 260;
const PADDING = 28;

function isFiniteNumber(value) {
  return value !== null && value !== undefined && Number.isFinite(Number(value));
}

function formatNumber(value) {
  if (!isFiniteNumber(value)) {
    return '-';
  }
  return new Intl.NumberFormat('ko-KR', { maximumFractionDigits: 2 }).format(Number(value));
}

function formatDate(value) {
  return new Date(value).toLocaleString('ko-KR', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function StockChart({ points = [], currency }) {
  const svgRef = useRef(null);
  const [hoverIndex, setHoverIndex] = useState(null);
  const chartData = useMemo(
    () => points.filter((point) => isFiniteNumber(point.close)).map((point) => ({ ...point, close: Number(point.close) })),
    [points],
  );

  const chart = useMemo(() => {
    if (chartData.length < 2) {
      return null;
    }
    const values = chartData.map((point) => point.close);
    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);
    const range = maxValue - minValue || 1;
    const toX = (index) => PADDING + (index / (chartData.length - 1)) * (WIDTH - PADDING * 2);
    const toY = (value) => HEIGHT - PADDING - ((value - minValue) / range) * (HEIGHT - PADDING * 2);
    const path = chartData.map((point, index) => `${toX(index)},${toY(point.close)}`).join(' ');
    const baseline = HEIGHT - PADDING;
    const fillPath = `${PADDING},${baseline} ${path} ${WIDTH - PADDING},${baseline}`;
    return { fillPath, maxValue, minValue, path, toX, toY };
  }, [chartData]);

  function handlePointerMove(event) {
    if (!svgRef.current || chartData.length < 2) {
      return;
    }
    const rect = svgRef.current.getBoundingClientRect();
    const ratio = Math.min(Math.max((event.clientX - rect.left) / rect.width, 0), 1);
    setHoverIndex(Math.round(ratio * (chartData.length - 1)));
  }

  if (!chart) {
    return <div className="chartEmpty">Not enough chart data.</div>;
  }

  const hoverPoint = hoverIndex === null ? chartData[chartData.length - 1] : chartData[hoverIndex];
  const hoverX = chart.toX(hoverIndex === null ? chartData.length - 1 : hoverIndex);
  const hoverY = chart.toY(hoverPoint.close);
  const tone = chartData[chartData.length - 1].close >= chartData[0].close ? 'positive' : 'negative';

  return (
    <div className="chartShell">
      <div className="chartHeader">
        <div>
          <strong>{formatNumber(hoverPoint.close)}</strong>
          <span>{currency}</span>
        </div>
        <span>{formatDate(hoverPoint.timestamp)}</span>
      </div>
      <svg
        aria-label="Price chart"
        className={`stockChart ${tone}`}
        onMouseLeave={() => setHoverIndex(null)}
        onMouseMove={handlePointerMove}
        ref={svgRef}
        role="img"
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      >
        <polygon className="chartFill" points={chart.fillPath} />
        <polyline className="chartLine" points={chart.path} />
        <line className="chartGuide" x1={PADDING} x2={WIDTH - PADDING} y1={PADDING} y2={PADDING} />
        <line className="chartGuide" x1={PADDING} x2={WIDTH - PADDING} y1={HEIGHT - PADDING} y2={HEIGHT - PADDING} />
        <line className="chartHoverLine" x1={hoverX} x2={hoverX} y1={PADDING} y2={HEIGHT - PADDING} />
        <circle className="chartHoverPoint" cx={hoverX} cy={hoverY} r="5" />
        <text className="chartAxisLabel" x={PADDING} y={PADDING - 8}>
          {formatNumber(chart.maxValue)}
        </text>
        <text className="chartAxisLabel" x={PADDING} y={HEIGHT - 8}>
          {formatNumber(chart.minValue)}
        </text>
      </svg>
    </div>
  );
}

export default StockChart;
