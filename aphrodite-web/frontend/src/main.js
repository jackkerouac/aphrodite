import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './store'
import './assets/tailwind.css'

// Create the app
const app = createApp(App)

// Use plugins
app.use(router)
app.use(pinia)

// Mount the app
app.mount('#app')
