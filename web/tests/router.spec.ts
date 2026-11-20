import { describe, expect, it } from 'vitest'
import { createMemoryHistory } from 'vue-router'
import { createAppRouter } from '../src/router'
import { DOMAIN_NAMES } from '../src/api/types'
import HomeView from '../src/views/HomeView.vue'
import WorksView from '../src/views/WorksView.vue'
import DomainPlaceholderView from '../src/views/DomainPlaceholderView.vue'
import NotFoundView from '../src/views/NotFoundView.vue'

describe('router', () => {
  it('resolves home, every domain, and NotFound', async () => {
    const router = createAppRouter(createMemoryHistory())

    await router.push('/')
    expect(router.currentRoute.value.name).toBe('home')
    expect(router.currentRoute.value.matched[0]?.components?.default).toBe(HomeView)

    await router.push('/works')
    expect(router.currentRoute.value.name).toBe('works')
    expect(router.currentRoute.value.matched[0]?.components?.default).toBe(WorksView)

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

  it('declares the works page plus exactly one placeholder route per backend domain', () => {
    const router = createAppRouter(createMemoryHistory())
    const named = router.getRoutes().map((route) => route.name).filter(String)
    expect(named).toHaveLength(2 + DOMAIN_NAMES.length + 1)
    expect(named).toContain('works')
    for (const domain of DOMAIN_NAMES) {
      expect(named).toContain(`domain-${domain}`)
    }
  })
})
