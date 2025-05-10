import React, { useState } from 'react';

interface SimplePosterImageProps {
  src: string; 
  alt?: string;
  width?: number;
  height?: number;
}

const SimplePosterImage: React.FC<SimplePosterImageProps> = ({ 
  src,
  alt = "Poster",
  width = 300,
  height
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  return (
    <div className="relative">
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full"></div>
        </div>
      )}
      
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-muted/10">
          <p className="text-destructive">Error loading image</p>
        </div>
      )}
      
      <img 
        src={src}
        alt={alt}
        width={width}
        height={height}
        onLoad={() => {
          console.log(`Image loaded successfully: ${src}`);
          setLoading(false);
        }}
        onError={(e) => {
          console.error(`Error loading image: ${src}`, e);
          setLoading(false);
          setError(true);
        }}
        style={{ 
          display: loading ? 'none' : 'block',
          maxWidth: '100%'
        }}
      />
    </div>
  );
};

export default SimplePosterImage;