import { useEffect, useMemo, useState } from 'react';

const SEARCH_ENDPOINT = '/api/v1/market/search';

function SettingsTab({ addedStocks, onAddStock, onRemoveStock, onOpenStock }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [message, setMessage] = useState('');
  const addedSymbols = useMemo(() => new Set(addedStocks.map((item) => item.providerSymbol)), [addedStocks]);

  useEffect(() => {
    const normalizedQuery = query.trim();
    if (!normalizedQuery) {
      setResults([]);
      setMessage('Enter a stock or ETF symbol/name.');
      setIsSearching(false);
      return undefined;
    }
    if (normalizedQuery.length > 50) {
      setResults([]);
      setMessage('Search text must be 50 characters or fewer.');
      setIsSearching(false);
      return undefined;
    }

    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      setIsSearching(true);
      setMessage('');
      try {
        const response = await fetch(`${SEARCH_ENDPOINT}?query=${encodeURIComponent(normalizedQuery)}`, {
          signal: controller.signal,
        });
        if (!response.ok) {
          throw new Error(`Search failed (${response.status})`);
        }
        const data = await response.json();
        setResults(data.results ?? []);
        if ((data.results ?? []).length === 0) {
          setMessage('No Korea/US stock or ETF results found.');
        }
      } catch (error) {
        if (error?.name !== 'AbortError') {
          setResults([]);
          setMessage(error instanceof Error ? error.message : 'Search failed.');
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsSearching(false);
        }
      }
    }, 300);

    return () => {
      controller.abort();
      window.clearTimeout(timer);
    };
  }, [query]);

  return (
    <section className="settingsLayout" aria-label="Settings">
      <div className="settingsPanel">
        <div className="sectionHeader">
          <div>
            <h2>Search stocks and ETFs</h2>
            <span>Korea and US listed stocks/ETFs only</span>
          </div>
        </div>
        <label className="searchField">
          <span>Symbol or name</span>
          <input
            autoComplete="off"
            maxLength={50}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="QLD, AAPL, 005930..."
            type="search"
            value={query}
          />
        </label>
        <div className="searchState">{isSearching ? 'Searching...' : message}</div>
        <div className="searchResults">
          {results.map((item) => {
            const isAdded = addedSymbols.has(item.providerSymbol);
            return (
              <article className="searchResult" key={item.providerSymbol}>
                <div>
                  <strong>{item.displaySymbol}</strong>
                  <span>{item.name}</span>
                  <small>
                    {item.country} · {item.exchange} · {item.instrumentType.toUpperCase()} · {item.currency}
                  </small>
                </div>
                <button type="button" onClick={() => (isAdded ? onOpenStock(item.providerSymbol) : onAddStock(item))}>
                  {isAdded ? 'Open' : 'Add'}
                </button>
              </article>
            );
          })}
        </div>
      </div>

      <div className="settingsPanel">
        <div className="sectionHeader">
          <div>
            <h2>Added tabs</h2>
            <span>{addedStocks.length} symbols</span>
          </div>
        </div>
        <div className="addedStockList">
          {addedStocks.length === 0 && <div className="emptyState">No stock tabs added yet.</div>}
          {addedStocks.map((item) => (
            <article className="addedStock" key={item.providerSymbol}>
              <button className="stockOpenButton" type="button" onClick={() => onOpenStock(item.providerSymbol)}>
                <strong>{item.displaySymbol}</strong>
                <span>{item.name}</span>
              </button>
              <button className="ghostButton" type="button" onClick={() => onRemoveStock(item.providerSymbol)}>
                Remove
              </button>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

export default SettingsTab;
