import type { NextConfig } from "next";

// Get API URL from environment or default to localhost for development
const getApiUrl = () => {
  // In production (Docker), use relative URLs so they work with any hostname
  if (process.env.NODE_ENV === 'production') {
    return '';
  }
  // In development, use localhost
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
};

const nextConfig: NextConfig = {
  // Skip linting and type checking during Docker builds
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  async rewrites() {
    const apiUrl = getApiUrl();
    
    // In production, don't rewrite since API is served from same host
    if (process.env.NODE_ENV === 'production') {
      return [];
    }
    
    // In development, rewrite to API server
    return [
      {
        source: "/api/:path*",
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
  images: {
    remotePatterns: [
      // Only allow localhost since we're using image proxy
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000',
        pathname: '/**',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'http',
        hostname: '127.0.0.1',
        port: '8000',
        pathname: '/**',
      },
      {
        protocol: 'http',
        hostname: '127.0.0.1',
        port: '',
        pathname: '/**',
      },
      // External poster sources for Replace Poster feature
      {
        protocol: 'https',
        hostname: 'image.tmdb.org',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'm.media-amazon.com',
        pathname: '/**',
      },
      {
        protocol: 'http',
        hostname: 'm.media-amazon.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'ia.media-imdb.com',
        pathname: '/**',
      },
      {
        protocol: 'http',
        hostname: 'ia.media-imdb.com',
        pathname: '/**',
      }
    ],
  },
};

export default nextConfig;