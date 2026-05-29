function StatusBanner({ isLoading, errorMessage, isEmpty, onRetry }) {
  if (isLoading) {
    return <div className="statusBanner neutral">Loading market data...</div>;
  }

  if (errorMessage) {
    return (
      <div className="statusBanner danger">
        <span>{errorMessage}</span>
        <button type="button" onClick={onRetry}>
          Retry
        </button>
      </div>
    );
  }

  if (isEmpty) {
    return (
      <div className="statusBanner neutral">
        <span>No market data to display.</span>
        <button type="button" onClick={onRetry}>
          Reload
        </button>
      </div>
    );
  }

  return null;
}

export default StatusBanner;
