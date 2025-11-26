import React, { useState, useEffect } from 'react';
import {
  fetchCensusDatasets,
  fetchCensusVariables,
  fetchCensusGeographies,
  executeCensusQuery,
} from '../services/api';
import type {
  CensusDataset,
  CensusVariable,
  CensusGeography,
  CensusQueryRequest,
  CensusQueryResponse,
} from '../types/api';
import './CensusQueryBuilder.css';

interface CensusQueryBuilderProps {
  onQueryResult: (result: CensusQueryResponse) => void;
  onError: (error: string) => void;
}

const CensusQueryBuilder: React.FC<CensusQueryBuilderProps> = ({
  onQueryResult,
  onError,
}) => {
  const [loading, setLoading] = useState(false);
  
  // Dataset selection
  const [datasetType, setDatasetType] = useState<'year_based' | 'timeseries' | ''>('');
  const [datasets, setDatasets] = useState<CensusDataset[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<string>('');
  const [selectedYear, setSelectedYear] = useState<number | null>(null);
  
  // Variable selection
  const [variables, setVariables] = useState<CensusVariable[]>([]);
  const [selectedVariables, setSelectedVariables] = useState<string[]>([]);
  const [variableSearch, setVariableSearch] = useState('');
  
  // Geography selection
  const [geographies, setGeographies] = useState<CensusGeography[]>([]);
  const [selectedGeography, setSelectedGeography] = useState<string>('us:1');
  const [selectedState, setSelectedState] = useState<string>('');
  const [selectedCounty, setSelectedCounty] = useState<string>('');
  const [customGeography, setCustomGeography] = useState<string>('');
  
  // Time range (for timeseries)
  const [timeStart, setTimeStart] = useState<string>('2020-01-01');
  const [timeEnd, setTimeEnd] = useState<string>('2024-01-01');
  
  // Load datasets on mount
  useEffect(() => {
    loadDatasets();
  }, []);
  
  // Load variables when dataset changes
  useEffect(() => {
    if (selectedDataset) {
      loadVariables();
    }
  }, [selectedDataset, selectedYear]);
  
  // Load geographies when dataset changes
  useEffect(() => {
    if (selectedDataset) {
      loadGeographies();
    }
  }, [selectedDataset]);
  
  const loadDatasets = async () => {
    try {
      setLoading(true);
      const response = await fetchCensusDatasets();
      setDatasets(response.datasets);
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to load datasets');
    } finally {
      setLoading(false);
    }
  };
  
  const loadVariables = async () => {
    try {
      setLoading(true);
      setVariables([]); // Clear previous variables
      const response = await fetchCensusVariables(selectedDataset, selectedYear || undefined);
      console.log('Variables response:', response);
      if (response.variables && response.variables.length > 0) {
        setVariables(response.variables);
      } else {
        console.warn('No variables returned from API');
        onError('No variables found for this dataset. The dataset may not support variable discovery, or you may need to enter variable names manually.');
      }
    } catch (err) {
      console.error('Error loading variables:', err);
      onError(err instanceof Error ? err.message : 'Failed to load variables');
      // Still set empty array so UI doesn't show stale data
      setVariables([]);
    } finally {
      setLoading(false);
    }
  };
  
  const loadGeographies = async () => {
    try {
      setLoading(true);
      const response = await fetchCensusGeographies(selectedDataset);
      setGeographies(response.geographies);
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to load geographies');
    } finally {
      setLoading(false);
    }
  };
  
  const handleDatasetTypeSelect = (type: 'year_based' | 'timeseries' | '') => {
    setDatasetType(type);
    setSelectedDataset('');
    setSelectedYear(null);
    setSelectedVariables([]);
    setVariables([]);
  };
  
  const handleDatasetSelect = (datasetId: string) => {
    setSelectedDataset(datasetId);
    setSelectedVariables([]);
    const dataset = datasets.find(d => d.id === datasetId);
    if (dataset && dataset.years && dataset.years.length > 0) {
      setSelectedYear(Math.max(...dataset.years));
    } else {
      setSelectedYear(null);
    }
  };
  
  const handleVariableToggle = (variableId: string) => {
    setSelectedVariables(prev =>
      prev.includes(variableId)
        ? prev.filter(id => id !== variableId)
        : [...prev, variableId]
    );
  };
  
  const handleGeographySelect = (geoId: string) => {
    setSelectedGeography(geoId);
    if (geoId !== 'state:*' && !geoId.startsWith('state:')) {
      setSelectedState('');
    }
    if (geoId !== 'county:*' && !geoId.startsWith('county:')) {
      setSelectedCounty('');
    }
  };
  
  const buildGeographyString = (): string => {
    if (customGeography) {
      return customGeography;
    }
    if (selectedGeography === 'state:*' && selectedState) {
      return `state:${selectedState}`;
    }
    if (selectedGeography === 'county:*' && selectedState && selectedCounty) {
      return `county:${selectedCounty} in state:${selectedState}`;
    }
    return selectedGeography;
  };
  
  const handleExecuteQuery = async () => {
    if (!selectedDataset || selectedVariables.length === 0) {
      onError('Please select a dataset and at least one variable');
      return;
    }
    
    try {
      setLoading(true);
      const query: CensusQueryRequest = {
        dataset: selectedDataset,
        variables: selectedVariables,
        geography: buildGeographyString(),
      };
      
      if (datasetType === 'year_based' && selectedYear) {
        query.year = selectedYear;
      }
      
      if (datasetType === 'timeseries') {
        query.time_range = {
          start: timeStart,
          end: timeEnd,
        };
      }
      
      const result = await executeCensusQuery(query);
      onQueryResult(result);
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to execute query');
    } finally {
      setLoading(false);
    }
  };
  
  const filteredVariables = variables.filter(v =>
    v.id.toLowerCase().includes(variableSearch.toLowerCase()) ||
    v.name.toLowerCase().includes(variableSearch.toLowerCase())
  );
  
  const filteredDatasets = datasets.filter(d => {
    if (datasetType === 'year_based') {
      return !d.id.startsWith('timeseries');
    }
    if (datasetType === 'timeseries') {
      return d.id.startsWith('timeseries');
    }
    return true;
  });
  
  return (
    <div className="census-query-builder">
      <div className="query-builder-header">
        <h3>Census Bureau Query Builder</h3>
      </div>
      
      {loading && <div className="loading-overlay">Loading...</div>}
      
      <div className="query-form">
        {/* Dataset Type Selection */}
        <div className="form-section">
          <label>Dataset Type:</label>
          <select
            value={datasetType}
            onChange={(e) => handleDatasetTypeSelect(e.target.value as 'year_based' | 'timeseries' | '')}
            className="form-select"
          >
            <option value="">-- Select dataset type --</option>
            <option value="year_based">Year-Based Dataset (e.g., Population Estimates, ACS)</option>
            <option value="timeseries">Time Series Dataset (e.g., Economic Indicators)</option>
          </select>
        </div>
        
        {/* Dataset Selection */}
        {datasetType && (
          <div className="form-section">
            <label>Dataset:</label>
            <select
              value={selectedDataset}
              onChange={(e) => handleDatasetSelect(e.target.value)}
              className="form-select"
            >
              <option value="">-- Select a dataset --</option>
              {filteredDatasets.map(dataset => (
                <option key={dataset.id} value={dataset.id}>
                  {dataset.name}
                </option>
              ))}
            </select>
          </div>
        )}
        
        {/* Year Selection (for year-based datasets) */}
        {selectedDataset && datasetType === 'year_based' && (
          <div className="form-section">
            <label>Year:</label>
            <select
              value={selectedYear || ''}
              onChange={(e) => setSelectedYear(parseInt(e.target.value))}
              className="form-select"
            >
              <option value="">-- Select year --</option>
              {datasets
                .find(d => d.id === selectedDataset)
                ?.years?.map(year => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
            </select>
          </div>
        )}
        
        {/* Variable Selection */}
        {selectedDataset && (datasetType === 'timeseries' || selectedYear) && (
          <div className="form-section">
            <label>Variables:</label>
            {variables.length === 0 && !loading && (
              <div className="variable-manual-entry">
                <p className="manual-entry-note">
                  Variable discovery is not available for this dataset. Please enter variable names manually (comma-separated):
                </p>
                <input
                  type="text"
                  placeholder="e.g., POP, BIRTHS or EMPSALUS, RETAILUS"
                  value={variableSearch}
                  onChange={(e) => {
                    setVariableSearch(e.target.value);
                    // Parse comma-separated variables
                    const vars = e.target.value.split(',').map(v => v.trim()).filter(v => v);
                    setSelectedVariables(vars);
                  }}
                  className="manual-variable-input"
                />
                <p className="manual-entry-help">
                  <a href="https://www.census.gov/data/developers/data-sets.html" target="_blank" rel="noopener noreferrer">
                    Browse available variables in Census documentation
                  </a>
                </p>
              </div>
            )}
            {variables.length > 0 && (
              <>
                <div className="variable-search">
                  <input
                    type="text"
                    placeholder="Search variables..."
                    value={variableSearch}
                    onChange={(e) => setVariableSearch(e.target.value)}
                    className="search-input"
                  />
                </div>
                <div className="variable-list">
                  {filteredVariables.length === 0 ? (
                    <p className="variable-list-empty">
                      No variables match your search. Try a different search term.
                    </p>
                  ) : (
                    filteredVariables.map(variable => (
                      <label key={variable.id} className="variable-item">
                        <input
                          type="checkbox"
                          checked={selectedVariables.includes(variable.id)}
                          onChange={() => handleVariableToggle(variable.id)}
                        />
                        <div className="variable-info">
                          <strong>{variable.id}</strong>
                          <span>{variable.name}</span>
                          {variable.description && (
                            <small>{variable.description}</small>
                          )}
                        </div>
                      </label>
                    ))
                  )}
                </div>
              </>
            )}
            {selectedVariables.length > 0 && (
              <div className="selected-variables">
                <strong>Selected ({selectedVariables.length}):</strong>
                <div className="variable-chips">
                  {selectedVariables.map(vid => (
                    <span key={vid} className="variable-chip">
                      {vid}
                      <button onClick={() => handleVariableToggle(vid)}>×</button>
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
        
        {/* Geography Selection */}
        {selectedVariables.length > 0 && (
          <div className="form-section">
            <label>Geography:</label>
            <select
              value={selectedGeography}
              onChange={(e) => handleGeographySelect(e.target.value)}
              className="form-select"
            >
              {geographies.map(geo => (
                <option key={geo.id} value={geo.id}>
                  {geo.name}
                </option>
              ))}
            </select>
            
            {selectedGeography === 'state:*' && (
              <div className="state-selector">
                <label>State FIPS Code:</label>
                <input
                  type="text"
                  placeholder="e.g., 06 for California"
                  value={selectedState}
                  onChange={(e) => setSelectedState(e.target.value)}
                  className="fips-input"
                />
              </div>
            )}
            
            {selectedGeography === 'county:*' && (
              <div className="county-selector">
                <label>State FIPS Code:</label>
                <input
                  type="text"
                  placeholder="e.g., 06"
                  value={selectedState}
                  onChange={(e) => setSelectedState(e.target.value)}
                  className="fips-input"
                />
                <label>County FIPS Code:</label>
                <input
                  type="text"
                  placeholder="e.g., 037"
                  value={selectedCounty}
                  onChange={(e) => setSelectedCounty(e.target.value)}
                  className="fips-input"
                />
              </div>
            )}
            
            <div className="custom-geography">
              <label>Or enter custom geography:</label>
              <input
                type="text"
                placeholder="e.g., state:06, county:001 in state:06"
                value={customGeography}
                onChange={(e) => setCustomGeography(e.target.value)}
                className="custom-geo-input"
              />
            </div>
          </div>
        )}
        
        {/* Time Range (Timeseries only) */}
        {selectedVariables.length > 0 && datasetType === 'timeseries' && (
          <div className="form-section">
            <label>Time Range:</label>
            <div className="time-range-selector">
              <div className="date-input-group">
                <label>Start Date:</label>
                <input
                  type="date"
                  value={timeStart}
                  onChange={(e) => setTimeStart(e.target.value)}
                  className="date-input"
                />
              </div>
              <div className="date-input-group">
                <label>End Date:</label>
                <input
                  type="date"
                  value={timeEnd}
                  onChange={(e) => setTimeEnd(e.target.value)}
                  className="date-input"
                />
              </div>
            </div>
          </div>
        )}
        
        {/* Execute Button */}
        {selectedVariables.length > 0 && 
         selectedGeography && 
         (datasetType === 'timeseries' ? (timeStart && timeEnd) : (datasetType === 'year_based' ? selectedYear : true)) && (
          <div className="form-section form-actions">
            <button
              onClick={handleExecuteQuery}
              className="execute-button"
              disabled={loading}
            >
              {loading ? 'Executing Query...' : 'Execute Query'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CensusQueryBuilder;

