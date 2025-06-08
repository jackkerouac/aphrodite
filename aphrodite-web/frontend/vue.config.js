/**
 * Development proxy configuration for Vue CLI
 * Proxies API calls from frontend dev server to backend server
 */

module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:2125',
        changeOrigin: true,
        secure: false,
        logLevel: 'debug'
      }
    },
    port: 8080,
    host: 'localhost'
  }
}
