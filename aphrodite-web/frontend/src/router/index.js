import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/analytics',
    name: 'analytics',
    component: () => import('../views/DatabaseView.vue')
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
  },
  {
    path: '/schedules',
    name: 'schedules',
    component: () => import('../views/SchedulesView.vue')
  },
  {
    path: '/poster-manager',
    name: 'poster-manager',
    component: () => import('../views/PosterManagerView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
