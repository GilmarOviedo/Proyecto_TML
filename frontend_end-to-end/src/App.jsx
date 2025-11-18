import { useState, useEffect } from 'react';
import SearchBar from './components/SearchBar';
import ImageGrid from './components/ImageGrid';
import { searchImages, getStats, healthCheck } from './services/api';
import './styles/App.css';

function App() {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastQuery, setLastQuery] = useState('');
  const [totalImages, setTotalImages] = useState(0);
  const [isBackendReady, setIsBackendReady] = useState(false);

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const health = await healthCheck();
        if (health) {
          setIsBackendReady(true);
          const stats = await getStats();
          if (stats) {
            setTotalImages(stats.total_images);
          }
        }
      } catch (err) {
        setIsBackendReady(false);
      }
    };

    checkBackend();
  }, []);

  const handleSearch = async (query) => {
    setIsLoading(true);
    setError(null);
    setLastQuery(query);
    
    try {
      const data = await searchImages(query, 5);
      
      setResults(data.results);
      setTotalImages(data.total_images);
      
      if (data.results.length === 0) {
        setError('No se encontraron imagenes para esta busqueda.');
      }
    } catch (err) {
      if (err.code === 'ECONNABORTED') {
        setError('La busqueda tardo demasiado.');
      } else if (err.response?.status === 404) {
        setError('No hay imagenes indexadas en la base de datos.');
      } else if (err.response?.status === 500) {
        setError('Error en el servidor.');
      } else {
        setError('No se pudo conectar con el backend.');
      }
      
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <div className="header-content">
            <h1>CLIP Image Search</h1>
            <p className="subtitle">
              Busqueda <strong>semantica</strong> de imagenes usando <strong>Inteligencia Artificial</strong>
            </p>
            {isBackendReady && totalImages > 0 && (
              <div className="stats-badge">
                {totalImages.toLocaleString('es-ES')} imagenes indexadas
              </div>
            )}
            {!isBackendReady && (
              <div className="stats-badge" style={{ 
                background: 'rgba(255, 100, 100, 0.2)', 
                borderColor: 'rgba(255, 100, 100, 0.4)',
                color: '#ff6b6b'
              }}>
                Backend desconectado
              </div>
            )}
          </div>
        </header>

        <main className="main-content">
          <SearchBar onSearch={handleSearch} isLoading={isLoading} />
          
          {error && (
            <div className="error-message">
              <span className="error-icon">Alerta</span>
              <p>{error}</p>
            </div>
          )}

          {isLoading && (
            <div className="loading">
              <div className="spinner"></div>
              <p>Analizando con CLIP y buscando imagenes similares...</p>
            </div>
          )}

          {!isLoading && !error && results.length > 0 && (
            <ImageGrid results={results} query={lastQuery} />
          )}

          {!isLoading && !error && results.length === 0 && !lastQuery && (
            <div className="empty-state">
              <div className="empty-icon">Iniciar</div>
              <h3>Comienza tu busqueda</h3>
              <p>
                Escribe una descripcion y encuentra imagenes similares. Ejemplo: red car on highway, woman reading book, tropical beach
              </p>
            </div>
          )}
        </main>

        <footer className="footer">
          <p>
            Powered by <strong>OpenAI CLIP</strong> - <strong>FastAPI</strong> - <strong>React</strong> - <strong>PostgreSQL</strong>
          </p>
          <p style={{ marginTop: '10px', fontSize: '0.9em', opacity: 0.7 }}>
            Proyecto TML - End-to-End Image Search System
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;
