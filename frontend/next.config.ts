import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
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