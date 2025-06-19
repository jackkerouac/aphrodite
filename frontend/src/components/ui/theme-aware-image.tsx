'use client';

import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';
import Image from 'next/image';

interface ThemedImageProps {
  lightSrc: string;
  darkSrc: string;
  alt: string;
  width?: number;
  height?: number;
  className?: string;
}

export function ThemedImage({ 
  lightSrc, 
  darkSrc, 
  alt, 
  width, 
  height, 
  className 
}: ThemedImageProps) {
  const { theme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // useEffect only runs on the client, so now we can safely show the UI
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    // Return a placeholder during SSR to prevent hydration mismatch
    return (
      <div 
        className={className}
        style={{ 
          width: width || 32, 
          height: height || 32,
          backgroundColor: 'transparent'
        }}
      />
    );
  }

  const imageSrc = theme === 'dark' ? lightSrc : darkSrc;

  if (width && height) {
    return (
      <Image
        src={imageSrc}
        alt={alt}
        width={width}
        height={height}
        className={className}
      />
    );
  }

  return (
    <img
      src={imageSrc}
      alt={alt}
      className={className}
    />
  );
}
