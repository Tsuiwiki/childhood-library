import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory } from 'vue-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from '../src/App.vue'
import { useAudioPlayer } from '../src/composables/useAudioPlayer'
import { createAppRouter } from '../src/router'

describe('continuous playback across Vue routes', () => {
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

  it('keeps the same audio element, source and position while navigating', async () => {
    const router = createAppRouter(createMemoryHistory())
    await router.push('/works')
    await router.isReady()
    const wrapper = mount(App, { attachTo: document.body, global: { plugins: [router] } })
    const play = vi.spyOn(HTMLMediaElement.prototype, 'play')

    await wrapper.find('[data-work-id="CN-C01"]').trigger('click')
    await flushPromises()
    const originalAudio = wrapper.find('audio').element as HTMLAudioElement
    originalAudio.currentTime = 17
    expect(originalAudio.getAttribute('src')).toBe('/audio/CN-C01-original.mp3')
    expect(play).toHaveBeenCalledTimes(1)

    await router.push('/story')
    await flushPromises()
    expect(router.currentRoute.value.name).toBe('story')
    expect(wrapper.find('h1').text()).toContain('儿童故事馆')
    expect(wrapper.find('audio').element).toBe(originalAudio)
    expect(originalAudio.getAttribute('src')).toBe('/audio/CN-C01-original.mp3')
    expect(originalAudio.currentTime).toBe(17)
    expect(wrapper.find('.player-title').text()).toBe('让我们荡起双桨')

    await router.push('/library')
    await flushPromises()
    expect(wrapper.find('h1').text()).toContain('从一份资料')
    expect(wrapper.find('audio').element).toBe(originalAudio)
    expect(originalAudio.currentTime).toBe(17)
    expect(play).toHaveBeenCalledTimes(1)

    await router.push('/works')
    await flushPromises()
    expect(wrapper.find('audio').element).toBe(originalAudio)
    await wrapper.find('.player-close').trigger('click')
    await flushPromises()
    expect(wrapper.find('audio').attributes('src')).toBeUndefined()
    expect(wrapper.find('.audio-player').attributes('hidden')).not.toBeUndefined()
    wrapper.unmount()
  })
})
