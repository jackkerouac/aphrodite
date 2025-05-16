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
    return apiClient.get(`/api/config/${fileName}`)
  },
  
  updateConfig(fileName, config) {
    return apiClient.put(`/api/config/${fileName}`, { config })
  }
}
