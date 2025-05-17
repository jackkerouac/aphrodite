import axios from 'axios'

const baseURL = process.env.VUE_APP_API_URL || 'http://localhost:5000'

const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 10000
})

export default {
  getConfigFiles() {
    return apiClient.get('/api/config/')
  },
  
  getConfig(fileName) {
    return new Promise((resolve, reject) => {
      apiClient.get(`/api/config/${fileName}`)
        .then(response => {
          console.log('Raw API response:', JSON.stringify(response.data, null, 2));
          resolve(response);
        })
        .catch(error => {
          console.error('API error:', error);
          reject(error);
        });
    });
  },
  
  updateConfig(fileName, config) {
    return apiClient.put(`/api/config/${fileName}`, { config })
  },
  
  testJellyfinConnection(credentials) {
    return apiClient.post('/api/check/', credentials)
  }
}
