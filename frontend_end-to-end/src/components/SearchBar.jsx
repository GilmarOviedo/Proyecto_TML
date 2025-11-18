import { useState } from 'react';

export default function SearchBar({ onSearch, isLoading }) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="search-container">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Describe lo que buscas: bicycle on the road, sunset over mountains, dog playing in park..."
        className="search-input"
        disabled={isLoading}
        autoFocus
        maxLength={200}
      />
      <button 
        type="submit" 
        className="search-button"
        disabled={isLoading || !query.trim()}
      >
        <span>
          {isLoading ? 'Analizando...' : 'Buscar'}
        </span>
      </button>
    </form>
  );
}
