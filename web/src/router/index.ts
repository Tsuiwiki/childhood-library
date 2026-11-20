import {
  createRouter,
  createWebHistory,
  type Router,
  type RouterHistory,
  type RouteRecordRaw,
} from 'vue-router'
import { DOMAIN_NAMES } from '@/api/types'
import HomeView from '@/views/HomeView.vue'
import WorksView from '@/views/WorksView.vue'
import DomainPlaceholderView from '@/views/DomainPlaceholderView.vue'
import NotFoundView from '@/views/NotFoundView.vue'

const domainRoutes: RouteRecordRaw[] = DOMAIN_NAMES.map((domain) => ({
  path: `/${domain}`,
  name: `domain-${domain}`,
  component: DomainPlaceholderView,
  props: { domain },
}))

const routes: RouteRecordRaw[] = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/works', name: 'works', component: WorksView },
  ...domainRoutes,
  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundView },
]

export function createAppRouter(history?: RouterHistory): Router {
  return createRouter({ history: history ?? createWebHistory(import.meta.env.BASE_URL), routes })
}

export const router = createAppRouter()
