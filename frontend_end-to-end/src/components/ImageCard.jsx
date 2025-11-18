export default function ImageCard({ image }) {
  const similarityPercent = (image.similarity * 100).toFixed(2);
  
  const fileName = image.image_url.split('/').pop() || 'unknown.jpg';
  
  const displayName = fileName.length > 40 
    ? fileName.substring(0, 37) + '...' 
    : fileName;

  return (
    <div className="image-card">
      <div className="image-container">
        <img 
          src={image.image_url} 
          alt={displayName}
          loading="lazy"
          onError={(e) => {
            e.target.onerror = null;
            e.target.src = 'https://via.placeholder.com/340x340/001f1c/C8E100?text=Error+al+Cargar';
          }}
        />
        <div className="similarity-badge">
          {similarityPercent}%
        </div>
      </div>
      <div className="image-info">
        <p className="file-name" title={fileName}>
          {displayName}
        </p>
      </div>
    </div>
  );
}
