import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory } from 'vue-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from '../src/App.vue'
import HomeView from '../src/views/HomeView.vue'
import { useAudioPlayer } from '../src/composables/useAudioPlayer'
import { createAppRouter } from '../src/router'

beforeEach(() => {
  vi.spyOn(window, 'scrollTo').mockImplementation(() => {})
  vi.spyOn(HTMLMediaElement.prototype, 'play').mockResolvedValue()
  vi.spyOn(HTMLMediaElement.prototype, 'pause').mockImplementation(() => {})
  vi.spyOn(HTMLMediaElement.prototype, 'load').mockImplementation(() => {})
})

afterEach(async () => {
  useAudioPlayer().closePlayer()
  await flushPromises()
  vi.restoreAllMocks()
  document.body.classList.remove('audio-player-open', 'dialog-open')
  document.body.innerHTML = ''
})

describe('content-first home page', () => {
  it('shows eight real works with deep links instead of engineering placeholders', async () => {
    const router = createAppRouter(createMemoryHistory())
    await router.push('/')
    await router.isReady()
    const wrapper = mount(HomeView, { global: { plugins: [router] } })

    expect(wrapper.find('h1').text()).toContain('一首一首收进来')
    expect(wrapper.text()).not.toContain('工程骨架')
    expect(wrapper.text()).not.toContain('不加载任何曲目')
    expect(wrapper.findAll('.work-card')).toHaveLength(8)
    expect(wrapper.find('[data-work="CN-C01"] .work-cover').attributes('href')).toBe('/works?work=CN-C01')
    expect(wrapper.find('[data-work="CN-C01"] img').attributes('src')).toBe('/song-assets/CN-C01-cover.svg')
    expect(wrapper.find('[data-work="CN-C01"]').text()).toContain('让我们荡起双桨')
    expect(wrapper.findAll('.highlight')).toHaveLength(4)
    expect(wrapper.find('.highlight').text()).toContain('219')
    expect(wrapper.find('.boundary details').exists()).toBe(true)
  })

  it('plays a real recording from the home page and keeps it across routes', async () => {
    const router = createAppRouter(createMemoryHistory())
    await router.push('/')
    await router.isReady()
    const wrapper = mount(App, { attachTo: document.body, global: { plugins: [router] } })

    await wrapper.find('[data-play="CN-C01"]').trigger('click')
    await flushPromises()
    expect(wrapper.find('audio').attributes('src')).toBe('/audio/CN-C01-original.mp3')
    expect(wrapper.find('[data-play="CN-C01"]').attributes('aria-pressed')).toBe('true')

    await router.push('/music')
    await flushPromises()
    expect(wrapper.find('audio').attributes('src')).toBe('/audio/CN-C01-original.mp3')
    wrapper.unmount()
  })

  it('offers the new catalogue and source pages from the home page', async () => {
    const router = createAppRouter(createMemoryHistory())
    await router.push('/')
    await router.isReady()
    const wrapper = mount(HomeView, { global: { plugins: [router] } })

    const hrefs = wrapper.findAll('a').map((link) => link.attributes('href'))
    expect(hrefs).toContain('/music/catalog')
    expect(hrefs).toContain('/music/sources')
    expect(hrefs).toContain('/works')
  })
})
