import React, { useState, useEffect, useRef } from 'react';
import type { DataSource } from '../types/api';
import { getSuggestions, type SuggestionItem } from '../services/api';
import './AutocompleteInput.css';

interface AutocompleteInputProps {
  value: string;
  onChange: (value: string) => void;
  onKeyPress?: (e: React.KeyboardEvent) => void;
  placeholder?: string;
  disabled?: boolean;
  source: DataSource;
  className?: string;
}

const AutocompleteInput: React.FC<AutocompleteInputProps> = ({
  value,
  onChange,
  onKeyPress,
  placeholder,
  disabled,
  source,
  className = '',
}) => {
  const [suggestions, setSuggestions] = useState<SuggestionItem[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchSuggestions = async () => {
      if (!value.trim() || disabled) {
        setSuggestions([]);
        setShowSuggestions(false);
        return;
      }

      setLoading(true);
      try {
        const response = await getSuggestions(source, value, undefined, 20);
        setSuggestions(response.suggestions);
        setShowSuggestions(response.suggestions.length > 0);
        setSelectedIndex(-1);
      } catch (error) {
        console.error('Error fetching suggestions:', error);
        setSuggestions([]);
        setShowSuggestions(false);
      } finally {
        setLoading(false);
      }
    };

    // Debounce API calls
    const timeoutId = setTimeout(fetchSuggestions, 300);
    return () => clearTimeout(timeoutId);
  }, [value, source, disabled]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
    setShowSuggestions(true);
  };

  const handleInputFocus = () => {
    if (suggestions.length > 0) {
      setShowSuggestions(true);
    }
  };

  const handleInputBlur = () => {
    // Delay hiding suggestions to allow click on suggestion
    setTimeout(() => {
      setShowSuggestions(false);
    }, 200);
  };

  const handleSuggestionClick = (suggestion: SuggestionItem) => {
    onChange(suggestion.symbol);
    setShowSuggestions(false);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showSuggestions || suggestions.length === 0) {
      if (e.key === 'Enter' && onKeyPress) {
        onKeyPress(e);
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev < suggestions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : -1));
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
          handleSuggestionClick(suggestions[selectedIndex]);
        } else if (onKeyPress) {
          onKeyPress(e);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        setSelectedIndex(-1);
        break;
      default:
        if (e.key === 'Enter' && onKeyPress) {
          onKeyPress(e);
        }
    }
  };

  const getTypeLabel = (type: string): string => {
    const typeMap: Record<string, string> = {
      ticker: 'Ticker',
      stock: 'Stock',
      forex: 'Forex',
      crypto: 'Crypto',
      variable: 'Variable',
      index: 'Index',
      etf: 'ETF',
    };
    return typeMap[type] || type;
  };

  const getTypeClass = (type: string): string => {
    const classMap: Record<string, string> = {
      ticker: 'suggestion-type-ticker',
      stock: 'suggestion-type-stock',
      forex: 'suggestion-type-forex',
      crypto: 'suggestion-type-crypto',
      variable: 'suggestion-type-variable',
      index: 'suggestion-type-index',
      etf: 'suggestion-type-etf',
    };
    return classMap[type] || '';
  };

  return (
    <div className={`autocomplete-wrapper ${className}`}>
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={handleInputChange}
        onFocus={handleInputFocus}
        onBlur={handleInputBlur}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        className="autocomplete-input"
        autoComplete="off"
      />
      {loading && (
        <div className="autocomplete-loading">Loading suggestions...</div>
      )}
      {showSuggestions && suggestions.length > 0 && (
        <div ref={suggestionsRef} className="autocomplete-suggestions">
          {suggestions.map((suggestion, index) => (
            <div
              key={`${suggestion.symbol}-${index}`}
              className={`autocomplete-suggestion ${
                index === selectedIndex ? 'selected' : ''
              }`}
              onClick={() => handleSuggestionClick(suggestion)}
              onMouseEnter={() => setSelectedIndex(index)}
            >
              <span className="suggestion-symbol">{suggestion.symbol}</span>
              <span className={`suggestion-type ${getTypeClass(suggestion.type)}`}>
                {getTypeLabel(suggestion.type)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AutocompleteInput;

