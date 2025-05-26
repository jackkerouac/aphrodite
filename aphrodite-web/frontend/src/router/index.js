import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/settings',
    name: 'settings',
    // Lazy-loaded component
    component: () => import('../views/SettingsView.vue')
  },
  {
    path: '/execute',
    name: 'execute',
    component: () => import('../views/ExecuteView.vue')
  },
  {
    path: '/preview',
    name: 'preview',
    component: () => import('../views/PreviewView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
