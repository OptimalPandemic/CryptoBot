import { createWebHistory, createRouter } from 'vue-router'
import Auth from '../plugins/auth0'
import Home from '@/components/Home'

const routes = [
  {
    path: "/",
    name: "Home",
    component: Home,
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router;