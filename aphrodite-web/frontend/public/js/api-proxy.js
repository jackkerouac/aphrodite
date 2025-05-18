// Proxy script to fix CORS issues
// This script should be included in the frontend index.html

console.log('API Proxy script loaded');

// Override API endpoints before the app loads
window.USE_API_PROXY = true;

// Override the API base URL in case the app loads before this script
if (window.API_CLIENT_CONFIGURED) {
    console.log('Reconfiguring API client to use proxy');
    window.configureApiClient(true);
}
