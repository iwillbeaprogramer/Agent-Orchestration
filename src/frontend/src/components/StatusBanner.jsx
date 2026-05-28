function StatusBanner({ isLoading, errorMessage, isEmpty, onRetry }) {
  if (isLoading) {
    return <div className="statusBanner neutral">데이터를 불러오는 중입니다.</div>;
  }

  if (errorMessage) {
    return (
      <div className="statusBanner danger">
        <span>{errorMessage}</span>
        <button type="button" onClick={onRetry}>
          재시도
        </button>
      </div>
    );
  }

  if (isEmpty) {
    return (
      <div className="statusBanner neutral">
        <span>표시할 시장 데이터가 없습니다.</span>
        <button type="button" onClick={onRetry}>
          다시 조회
        </button>
      </div>
    );
  }

  return null;
}

export default StatusBanner;
