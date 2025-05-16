import { createApp } from 'vue'
import App from './App.vue'
import './assets/tailwind.css'

// Create the app
const app = createApp(App)

// Configure and mount the app
app.mount('#app')

// Comment out router and store until they're installed
// Will uncomment after you install the dependencies
/*
import router from './router'
import store from './store'
app.use(router)
app.use(store)
*/
