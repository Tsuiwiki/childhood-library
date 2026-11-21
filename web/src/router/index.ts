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
import LibraryIndexView from '@/views/LibraryIndexView.vue'
import MusicView from '@/views/MusicView.vue'
import AudioSourcesView from '@/views/AudioSourcesView.vue'
import ResearchHallView from '@/views/ResearchHallView.vue'
import SpecialtyView from '@/views/SpecialtyView.vue'
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
  { path: '/library', name: 'library', component: LibraryIndexView },
  { path: '/music', name: 'music', component: MusicView },
  { path: '/music/sources', name: 'music-sources', component: AudioSourcesView },
  { path: '/music/specialties/:id', name: 'specialty', component: SpecialtyView },
  { path: '/story', name: 'story', component: ResearchHallView, props: { hall: 'story' } },
  { path: '/poetry', name: 'poetry', component: ResearchHallView, props: { hall: 'poetry' } },
  ...domainRoutes,
  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundView },
]

const pageTitles: Record<string, string> = {
  works: '内部曲目与录音详情',
  library: '跨馆资料总览',
  music: '儿童音乐馆',
  'music-sources': '儿歌音源链接',
  story: '儿童故事馆',
  poetry: '古诗词馆',
  specialty: '音乐专题',
}

export function createAppRouter(history?: RouterHistory): Router {
  const appRouter = createRouter({
    history: history ?? createWebHistory(import.meta.env.BASE_URL),
    routes,
    scrollBehavior(to, _from, savedPosition) {
      if (savedPosition) return savedPosition
      if (to.hash) return { el: to.hash, top: 104 }
      return { top: 0 }
    },
  })
  appRouter.afterEach((to) => {
    const title = pageTitles[String(to.name)]
    if (title) document.title = `${title}｜童年书房`
  })
  return appRouter
}

export const router = createAppRouter()
