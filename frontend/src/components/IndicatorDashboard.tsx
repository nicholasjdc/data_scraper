import React, { useState, useEffect } from 'react';
import { fetchCommonIndicators, fetchSearchResults, fetchSeries, fetchSources } from '../services/api';
import { TimeSeriesGraph, normalizeTimeSeriesData } from '../modules/graph';
import type { TimeSeriesDataset } from '../modules/graph';
import type { MultipleSeriesResponse, SearchResponse, DataSource, DataSourceInfo, CensusQueryResponse } from '../types/api';
import LoadingSpinner from './LoadingSpinner';
import AutocompleteInput from './AutocompleteInput';
import CensusQueryBuilder from './CensusQueryBuilder';
import ProvenanceBadge from './ProvenanceBadge';
import AIAnalysisPanel from './AIAnalysisPanel';
import './IndicatorDashboard.css';

const IndicatorDashboard: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [datasets, setDatasets] = useState<TimeSeriesDataset[]>([]);

  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [orderBy, setOrderBy] = useState<string>('search_rank');
  const [sortOrder, setSortOrder] = useState<string>('desc');
  const [selectedSource, setSelectedSource] = useState<DataSource>('fred');
  const [sources, setSources] = useState<DataSourceInfo[]>([]);

  const [directEntrySymbol, setDirectEntrySymbol] = useState<string>('');
  const [directEntryLoading, setDirectEntryLoading] = useState(false);

  const [censusQueryResult, setCensusQueryResult] = useState<CensusQueryResponse | null>(null);

  useEffect(() => {
    const loadSources = async () => {
      try {
        const response = await fetchSources();
        setSources(response.sources);
      } catch (err) {
        console.error('Failed to load sources:', err);
      }
    };
    loadSources();
  }, []);

  const currentSourceInfo = sources.find(s => s.id === selectedSource);
  const supportsSearch = currentSourceInfo?.supports_search ?? false;

  // Collect all fetch_ids from loaded datasets for AI analysis
  const allFetchIds = datasets
    .map(ds => ds.metadata?.fetch_id as string | undefined)
    .filter((id): id is string => Boolean(id));

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setSearchLoading(true);
    setSearchError(null);
    setSearchResults(null);
    try {
      const response = await fetchSearchResults({
        q: searchQuery.trim(),
        source: selectedSource,
        limit: 20,
        order_by: orderBy,
        sort_order: sortOrder,
      });
      setSearchResults(response);
    } catch (err) {
      setSearchError(err instanceof Error ? err.message : 'Failed to search series');
    } finally {
      setSearchLoading(false);
    }
  };

  const handleFetchSeries = async (seriesId: string, source?: DataSource) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchSeries(seriesId, { source: source || selectedSource });

      const graphData: TimeSeriesDataset = {
        id: `${response.source || 'fred'}_${response.series_id}`,
        label: response.title,
        data: normalizeTimeSeriesData(response.data),
        metadata: {
          units: response.units,
          frequency: response.frequency,
          source: response.source || 'fred',
          series_id: response.series_id,
          fetch_id: response.fetch_id,
          fetched_at: response.fetched_at,
        },
      };

      setDatasets(prev => {
        const exists = prev.some(ds => ds.id === graphData.id);
        return exists ? prev : [...prev, graphData];
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch series');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveGraph = (seriesId: string) => {
    setDatasets(prev => prev.filter(ds => ds.id !== seriesId));
  };

  const handleDirectEntry = async () => {
    if (!directEntrySymbol.trim()) return;
    setDirectEntryLoading(true);
    setError(null);
    try {
      await handleFetchSeries(directEntrySymbol.trim(), selectedSource);
      setDirectEntrySymbol('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setDirectEntryLoading(false);
    }
  };

  const getSourceGuidance = (): string => {
    switch (selectedSource) {
      case 'yfinance': return 'Enter ticker symbols (e.g., AAPL, MSFT, ^GSPC for S&P 500)';
      case 'alphavantage': return 'Enter forex pairs (e.g., EUR/USD, GBP/USD)';
      case 'census': return 'Enter variable names from Census datasets';
      case 'edgar': return 'Enter TICKER:CONCEPT (e.g., AAPL:Revenues, MSFT:NetIncomeLoss)';
      case 'oecd': return 'Enter DATASET:KEY (e.g., QNA:USA.B1_GS1.GYSA.Q, MEI:USA.LRHUTTTT.ST.M)';
      case 'ecb': return 'Enter FLOW/KEY (e.g., FM/B.U2.EUR.RT0.BB.1000.00.MRR_FR.AN)';
      default: return 'Enter symbol or series ID';
    }
  };

  const handleFetchIndicators = async () => {
    setLoading(true);
    setError(null);
    setDatasets([]);
    try {
      const response: MultipleSeriesResponse = await fetchCommonIndicators();

      const graphData: TimeSeriesDataset[] = Object.entries(response.series).map(([id, series]) => ({
        id,
        label: series.title,
        data: normalizeTimeSeriesData(series.data),
        metadata: {
          units: series.units,
          frequency: series.frequency,
          source: response.source || 'fred',
          series_id: id,
          fetch_id: series.fetch_id,
          fetched_at: series.fetched_at,
        },
      }));

      setDatasets(graphData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch indicators');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="indicator-dashboard">
      <header className="dashboard-header">
        <h1>Economic Data Dashboard</h1>
        <p>View economic data from multiple sources: FRED, Yahoo Finance, World Bank, Census Bureau, SEC EDGAR, OECD, and ECB</p>
      </header>

      <div className="search-section">
        <div className="search-controls">
          <div className="source-selector-group">
            <label htmlFor="source-select">Data Source:</label>
            <select
              id="source-select"
              value={selectedSource}
              onChange={e => {
                setSelectedSource(e.target.value as DataSource);
                setSearchResults(null);
                setDirectEntrySymbol('');
                setSearchError(null);
              }}
              className="source-select"
              disabled={searchLoading || directEntryLoading}
            >
              {sources.map(source => (
                <option key={source.id} value={source.id}>{source.name}</option>
              ))}
            </select>
          </div>
        </div>

        {supportsSearch ? (
          <>
            <div className="search-controls">
              <input
                type="text"
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                onKeyPress={e => { if (e.key === 'Enter') handleSearch(); }}
                placeholder="Search for economic data series..."
                className="search-input"
                disabled={searchLoading}
              />
              <button
                onClick={handleSearch}
                disabled={searchLoading || !searchQuery.trim()}
                className="search-button"
              >
                {searchLoading ? 'Searching...' : 'Search'}
              </button>
            </div>
            <div className="search-filters">
              <div className="filter-group">
                <label htmlFor="order-by-select">Order By:</label>
                <select
                  id="order-by-select"
                  value={orderBy}
                  onChange={e => setOrderBy(e.target.value)}
                  className="filter-select"
                  disabled={searchLoading}
                >
                  <option value="search_rank">Search Rank</option>
                  <option value="series_id">Series ID</option>
                  <option value="title">Title</option>
                  <option value="units">Units</option>
                  <option value="frequency">Frequency</option>
                </select>
              </div>
              <div className="filter-group">
                <label htmlFor="sort-order-select">Sort Order:</label>
                <select
                  id="sort-order-select"
                  value={sortOrder}
                  onChange={e => setSortOrder(e.target.value)}
                  className="filter-select"
                  disabled={searchLoading}
                >
                  <option value="desc">Descending</option>
                  <option value="asc">Ascending</option>
                </select>
              </div>
            </div>

            {searchError && (
              <div className="error-message"><p>Search Error: {searchError}</p></div>
            )}

            {searchResults && (
              <div className="search-results">
                <h2 className="search-results-header">
                  Search Results ({searchResults.count})
                  {searchResults.message && (
                    <span className="search-message">{searchResults.message}</span>
                  )}
                </h2>
                {searchResults.results.length === 0 && searchResults.message && (
                  <div className="search-no-results"><p>{searchResults.message}</p></div>
                )}
                <div className="search-results-list">
                  {searchResults.results.map(result => (
                    <div key={result.series_id} className="search-result-card">
                      <div className="search-result-header">
                        <h3 className="search-result-title">{result.title}</h3>
                        <span className="source-badge">{selectedSource}</span>
                      </div>
                      <div className="search-result-metadata">
                        <span className="metadata-item"><strong>Series ID:</strong> {result.series_id}</span>
                        <span className="metadata-item"><strong>Units:</strong> {result.units || 'N/A'}</span>
                        <span className="metadata-item"><strong>Frequency:</strong> {result.frequency || 'N/A'}</span>
                        <span className="metadata-item"><strong>Seasonal Adjustment:</strong> {result.seasonal_adjustment || 'N/A'}</span>
                        {result.popularity !== undefined && (
                          <span className="metadata-item"><strong>Popularity:</strong> {result.popularity}</span>
                        )}
                      </div>
                      <button
                        onClick={() => handleFetchSeries(result.series_id, selectedSource)}
                        className="fetch-data-button"
                        disabled={loading}
                      >
                        Fetch Data
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        ) : selectedSource === 'census' ? (
          <CensusQueryBuilder
            onQueryResult={result => {
              setCensusQueryResult(result);
              if (result.data && result.data.length > 0) {
                const timeColumn = result.headers.find(h => h.toLowerCase() === 'time');
                if (timeColumn) {
                  result.variables.forEach(variable => {
                    const dataPoints = result.data
                      .map(row => {
                        const timeStr = row[timeColumn] as string;
                        const value = row[variable];
                        if (timeStr && value !== null && value !== undefined) {
                          try {
                            return {
                              date: timeStr.length === 4 ? `${timeStr}-01-01` : timeStr,
                              value: parseFloat(value as string),
                            };
                          } catch { return null; }
                        }
                        return null;
                      })
                      .filter((dp): dp is { date: string; value: number } => dp !== null);

                    if (dataPoints.length > 0) {
                      const graphData: TimeSeriesDataset = {
                        id: `census_${result.dataset}_${variable}`,
                        label: `Census: ${variable} (${result.dataset})`,
                        data: normalizeTimeSeriesData(dataPoints),
                        metadata: {
                          units: '',
                          frequency: result.dataset.startsWith('timeseries') ? 'Monthly' : 'Annual',
                          source: 'census',
                          series_id: variable,
                          fetch_id: result.fetch_id,
                          fetched_at: result.fetched_at,
                        },
                      };
                      setDatasets(prev => {
                        const exists = prev.some(ds => ds.id === graphData.id);
                        return exists ? prev : [...prev, graphData];
                      });
                    }
                  });
                }
              }
            }}
            onError={err => setSearchError(err)}
          />
        ) : (
          <div className="direct-entry-section">
            <div className="direct-entry-controls">
              <AutocompleteInput
                value={directEntrySymbol}
                onChange={setDirectEntrySymbol}
                onKeyPress={e => { if (e.key === 'Enter') handleDirectEntry(); }}
                placeholder={getSourceGuidance()}
                disabled={directEntryLoading || loading}
                source={selectedSource}
                className="direct-entry-autocomplete"
              />
              <button
                onClick={handleDirectEntry}
                disabled={directEntryLoading || loading || !directEntrySymbol.trim()}
                className="direct-entry-button"
              >
                {directEntryLoading ? 'Fetching...' : 'Fetch Data'}
              </button>
            </div>
            <div className="direct-entry-help">
              <p className="direct-entry-guidance">{getSourceGuidance()}</p>
              {selectedSource === 'yfinance' && (
                <div className="direct-entry-examples">
                  <strong>Examples:</strong> AAPL (Apple), MSFT (Microsoft), ^GSPC (S&P 500), ^DJI (Dow Jones)
                </div>
              )}
              {selectedSource === 'alphavantage' && (
                <div className="direct-entry-examples">
                  <strong>Examples:</strong> EUR/USD, GBP/USD, USD/JPY, CHF/USD
                </div>
              )}
              {selectedSource === 'edgar' && (
                <div className="direct-entry-examples">
                  <strong>Examples:</strong> AAPL:Revenues, MSFT:NetIncomeLoss, TSLA:EarningsPerShareBasic, AMZN:Assets
                </div>
              )}
              {selectedSource === 'oecd' && (
                <div className="direct-entry-examples">
                  <strong>Examples:</strong> QNA:USA.B1_GS1.GYSA.Q (US GDP), MEI:USA.LRHUTTTT.ST.M (US unemployment), PRICES_CPI:DEU.CPALTT01.GY.M (Germany CPI)
                </div>
              )}
              {selectedSource === 'ecb' && (
                <div className="direct-entry-examples">
                  <strong>Examples:</strong> FM/B.U2.EUR.RT0.BB.1000.00.MRR_FR.AN (ECB rate), ICP/M.U2.N.000000.4.ANR (HICP), EXR/D.USD.EUR.SP00.A (USD/EUR)
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="dashboard-controls">
        <button onClick={handleFetchIndicators} disabled={loading} className="fetch-button">
          {loading ? 'Fetching...' : 'Fetch Indicators'}
        </button>
      </div>

      {loading && <LoadingSpinner />}

      {error && (
        <div className="error-message"><p>Error: {error}</p></div>
      )}

      {datasets.length > 0 && (
        <div className="graphs-container">
          {datasets.map(dataset => (
            <div key={dataset.id} className="graph-card">
              <div className="graph-header">
                <div className="graph-header-content">
                  <h3>{dataset.label}</h3>
                  <button
                    onClick={() => handleRemoveGraph(dataset.id)}
                    className="remove-graph-button"
                    title="Remove graph"
                  >
                    ×
                  </button>
                </div>
                <div className="graph-metadata">
                  <span className="metadata-item">
                    Units: {dataset.metadata?.units || 'N/A'}
                  </span>
                  <span className="metadata-item">
                    Frequency: {dataset.metadata?.frequency || 'N/A'}
                  </span>
                  <span className="metadata-item">
                    Data Points: {dataset.data.length}
                  </span>
                  {(dataset.metadata?.fetch_id != null && dataset.metadata?.fetched_at != null) && (
                    <span className="metadata-item">
                      <ProvenanceBadge
                        fetchId={String(dataset.metadata.fetch_id)}
                        fetchedAt={String(dataset.metadata.fetched_at)}
                        source={String(dataset.metadata.source ?? 'unknown')}
                        seriesId={String(dataset.metadata.series_id ?? dataset.id)}
                      />
                    </span>
                  )}
                </div>
              </div>
              <div className="graph-wrapper">
                <TimeSeriesGraph datasets={[dataset]} chartType="line" />
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && !error && datasets.length === 0 && (
        <div className="empty-state">
          <p>Click "Fetch Indicators" to load economic data</p>
        </div>
      )}

      {censusQueryResult && (
        <div className="census-results">
          <h3>Census Query Results</h3>
          <div className="census-results-info">
            <p><strong>Dataset:</strong> {censusQueryResult.dataset}</p>
            {censusQueryResult.year && <p><strong>Year:</strong> {censusQueryResult.year}</p>}
            <p><strong>Geography:</strong> {censusQueryResult.geography}</p>
            <p><strong>Variables:</strong> {censusQueryResult.variables.join(', ')}</p>
            <p><strong>Records:</strong> {censusQueryResult.count}</p>
            {censusQueryResult.fetch_id && censusQueryResult.fetched_at && (
              <div style={{ marginTop: '8px' }}>
                <ProvenanceBadge
                  fetchId={censusQueryResult.fetch_id}
                  fetchedAt={censusQueryResult.fetched_at}
                  source="census"
                  seriesId={censusQueryResult.dataset}
                />
              </div>
            )}
          </div>
          <div className="census-table-container">
            <table className="census-table">
              <thead>
                <tr>
                  {censusQueryResult.headers.map(header => (
                    <th key={header}>{header}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {censusQueryResult.data.slice(0, 100).map((row, idx) => (
                  <tr key={idx}>
                    {censusQueryResult.headers.map(header => (
                      <td key={header}>{String(row[header] ?? '')}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {censusQueryResult.data.length > 100 && (
              <p className="census-table-note">
                Showing first 100 of {censusQueryResult.data.length} records
              </p>
            )}
          </div>
        </div>
      )}

      <AIAnalysisPanel fetchIds={allFetchIds} />
    </div>
  );
};

export default IndicatorDashboard;
