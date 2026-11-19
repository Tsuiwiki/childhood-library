import { describe, expect, it } from 'vitest'
import { createMemoryHistory } from 'vue-router'
import { createAppRouter } from '../src/router'
import { DOMAIN_NAMES } from '../src/api/types'
import HomeView from '../src/views/HomeView.vue'
import DomainPlaceholderView from '../src/views/DomainPlaceholderView.vue'
import NotFoundView from '../src/views/NotFoundView.vue'

describe('router', () => {
  it('resolves home, every domain, and NotFound', async () => {
    const router = createAppRouter(createMemoryHistory())

    await router.push('/')
    expect(router.currentRoute.value.name).toBe('home')
    expect(router.currentRoute.value.matched[0]?.components?.default).toBe(HomeView)

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

  it('declares exactly one placeholder route per backend domain', () => {
    const router = createAppRouter(createMemoryHistory())
    const named = router.getRoutes().map((route) => route.name).filter(String)
    expect(named).toHaveLength(1 + DOMAIN_NAMES.length + 1)
    for (const domain of DOMAIN_NAMES) {
      expect(named).toContain(`domain-${domain}`)
    }
  })
})
