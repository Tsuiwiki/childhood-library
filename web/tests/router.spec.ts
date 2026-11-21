import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory } from 'vue-router'
import { createAppRouter } from '../src/router'
import { DOMAIN_NAMES } from '../src/api/types'
import HomeView from '../src/views/HomeView.vue'
import WorksView from '../src/views/WorksView.vue'
import LibraryIndexView from '../src/views/LibraryIndexView.vue'
import MusicView from '../src/views/MusicView.vue'
import AudioSourcesView from '../src/views/AudioSourcesView.vue'
import ResearchHallView from '../src/views/ResearchHallView.vue'
import SpecialtyView from '../src/views/SpecialtyView.vue'
import DomainPlaceholderView from '../src/views/DomainPlaceholderView.vue'
import NotFoundView from '../src/views/NotFoundView.vue'

beforeEach(() => {
  vi.spyOn(window, 'scrollTo').mockImplementation(() => {})
})

describe('router', () => {
  it('resolves home, museum halls, specialties, every domain, and NotFound', async () => {
    const router = createAppRouter(createMemoryHistory())

    await router.push('/')
    expect(router.currentRoute.value.name).toBe('home')
    expect(router.currentRoute.value.matched[0]?.components?.default).toBe(HomeView)

    await router.push('/works')
    expect(router.currentRoute.value.name).toBe('works')
    expect(router.currentRoute.value.matched[0]?.components?.default).toBe(WorksView)

    await router.push('/library')
    expect(router.currentRoute.value.name).toBe('library')
    expect(router.currentRoute.value.matched[0]?.components?.default).toBe(LibraryIndexView)

    await router.push('/music')
    expect(router.currentRoute.value.name).toBe('music')
    expect(router.currentRoute.value.matched[0]?.components?.default).toBe(MusicView)

    await router.push('/music/sources')
    expect(router.currentRoute.value.name).toBe('music-sources')
    expect(router.currentRoute.value.matched[0]?.components?.default).toBe(AudioSourcesView)

    await router.push('/music/specialties/childhood')
    expect(router.currentRoute.value.name).toBe('specialty')
    expect(router.currentRoute.value.params.id).toBe('childhood')
    expect(router.currentRoute.value.matched[0]?.components?.default).toBe(SpecialtyView)

    for (const hall of ['story', 'poetry'] as const) {
      await router.push(`/${hall}`)
      expect(router.currentRoute.value.name).toBe(hall)
      expect(router.currentRoute.value.matched[0]?.components?.default).toBe(ResearchHallView)
      expect(router.currentRoute.value.matched[0]?.props.default).toEqual({ hall })
    }

    for (const domain of DOMAIN_NAMES) {
      await router.push(`/${domain}`)
      expect(router.currentRoute.value.name).toBe(`domain-${domain}`)
      expect(router.currentRoute.value.matched[0]?.components?.default).toBe(DomainPlaceholderView)
      expect(router.currentRoute.value.matched[0]?.props.default).toEqual({ domain })
    }

    await router.push('/no-such-page')
    expect(router.currentRoute.value.name).toBe('not-found')
    expect(router.currentRoute.value.matched[0]?.components?.default).toBe(NotFoundView)
  })

  it('declares the frontend pages plus exactly one placeholder route per backend domain', () => {
    const router = createAppRouter(createMemoryHistory())
    const named = router.getRoutes().map((route) => route.name).filter(String)
    expect(named).toHaveLength(8 + DOMAIN_NAMES.length + 1)
    for (const name of ['works', 'library', 'music', 'music-sources', 'specialty', 'story', 'poetry']) {
      expect(named).toContain(name)
    }
    for (const domain of DOMAIN_NAMES) {
      expect(named).toContain(`domain-${domain}`)
    }
  })

  it('sets a readable page title after museum navigation', async () => {
    const router = createAppRouter(createMemoryHistory())
    await router.push('/poetry')
    await router.isReady()
    expect(document.title).toBe('古诗词馆｜童年书房')
  })
})
