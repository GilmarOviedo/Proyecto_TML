import ImageCard from './ImageCard';

export default function ImageGrid({ results, query }) {
  if (!results || results.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">Buscar</div>
        <h3>No se encontraron resultados</h3>
        <p>
          Intenta con diferentes terminos como: mountain landscape, cat sleeping, beach sunset, city at night
        </p>
      </div>
    );
  }

  return (
    <div className="results-section">
      <div className="results-header">
        <h2>
          Resultados para: <span className="query-highlight">{query}</span>
        </h2>
        <p className="results-count">
          {results.length} imagen{results.length !== 1 ? 'es' : ''} encontrada{results.length !== 1 ? 's' : ''} con alta similaridad
        </p>
      </div>
      <div className="image-grid">
        {results.map((image, index) => (
          <ImageCard key={image.id || index} image={image} />
        ))}
      </div>
    </div>
  );
}
