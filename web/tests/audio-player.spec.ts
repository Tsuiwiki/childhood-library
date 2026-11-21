import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import ClAudioPlayer, { type AudioPlayerTrack } from '../src/components/ClAudioPlayer.vue'

function localTrack(overrides: Partial<AudioPlayerTrack> = {}): AudioPlayerTrack {
  return {
    id: 'CN-C01',
    title: '让我们荡起双桨',
    source: 'audio/CN-C01-original.mp3',
    kicker: '内部经典录音 · 权利待核验 · 内部原型',
    fileLabel: '经典童声合唱（完整歌曲） · 内部研究试听',
    kind: 'sample',
    ...overrides,
  }
}

describe('ClAudioPlayer', () => {
  beforeEach(() => {
    vi.spyOn(HTMLMediaElement.prototype, 'play').mockResolvedValue()
    vi.spyOn(HTMLMediaElement.prototype, 'pause').mockImplementation(() => {})
    vi.spyOn(HTMLMediaElement.prototype, 'load').mockImplementation(() => {})
  })

  afterEach(() => {
    document.body.classList.remove('audio-player-open')
    document.body.innerHTML = ''
  })

  it('stays hidden without a track and opens with the original player content', async () => {
    const play = vi.spyOn(HTMLMediaElement.prototype, 'play')
    const wrapper = mount(ClAudioPlayer, { props: { track: null } })
    expect(wrapper.find('aside').attributes('hidden')).not.toBeUndefined()
    expect(play).not.toHaveBeenCalled()

    await wrapper.setProps({ track: localTrack() })
    await flushPromises()

    expect(wrapper.find('aside').attributes('hidden')).toBeUndefined()
    expect(wrapper.find('.player-title').text()).toBe('让我们荡起双桨')
    expect(wrapper.find('.player-kicker').text()).toContain('权利待核验')
    expect(wrapper.find('.player-file').text()).toContain('经典童声合唱')
    expect(wrapper.find('audio').attributes('src')).toBe('audio/CN-C01-original.mp3')
    expect(wrapper.find('audio').attributes('controls')).not.toBeUndefined()
    expect(wrapper.find('audio').attributes('preload')).toBe('metadata')
    expect(document.body.classList.contains('audio-player-open')).toBe(true)
    expect(play).toHaveBeenCalledTimes(1)
  })

  it('changes the source when another recording is selected', async () => {
    const pause = vi.spyOn(HTMLMediaElement.prototype, 'pause')
    const load = vi.spyOn(HTMLMediaElement.prototype, 'load')
    const wrapper = mount(ClAudioPlayer, { props: { track: localTrack() } })
    await flushPromises()

    await wrapper.setProps({
      track: localTrack({
        id: 'CN-C02',
        title: '我们的田野',
        source: 'audio/CN-C02-gxzf.flac',
      }),
    })
    await flushPromises()

    expect(wrapper.find('.player-title').text()).toBe('我们的田野')
    expect(wrapper.find('audio').attributes('src')).toBe('audio/CN-C02-gxzf.flac')
    expect(pause).toHaveBeenCalledTimes(2)
    expect(load).toHaveBeenCalledTimes(2)
  })

  it('closes by pausing, removing src, reloading, clearing errors and restoring focus', async () => {
    const trigger = document.createElement('button')
    trigger.dataset.audioPlay = ''
    trigger.dataset.workId = 'CN-C01'
    document.body.append(trigger)
    trigger.focus()

    const pause = vi.spyOn(HTMLMediaElement.prototype, 'pause')
    const load = vi.spyOn(HTMLMediaElement.prototype, 'load')
    const wrapper = mount(ClAudioPlayer, {
      props: { track: localTrack() },
      attachTo: document.body,
    })
    await flushPromises()
    vi.spyOn(HTMLMediaElement.prototype, 'play').mockRejectedValueOnce(new Error('blocked'))
    await wrapper.setProps({ track: localTrack({ source: 'audio/retry.mp3' }) })
    await flushPromises()
    expect(wrapper.find('.player-error').text()).not.toBe('')

    await wrapper.find('.player-close').trigger('click')

    expect(wrapper.emitted('close')).toHaveLength(1)
    expect(wrapper.find('aside').attributes('hidden')).not.toBeUndefined()
    expect(wrapper.find('audio').attributes('src')).toBeUndefined()
    expect(wrapper.find('.player-error').text()).toBe('')
    expect(wrapper.find('.player-error').attributes('hidden')).not.toBeUndefined()
    expect(document.body.classList.contains('audio-player-open')).toBe(false)
    expect(pause).toHaveBeenCalled()
    expect(load).toHaveBeenCalled()
    expect(document.activeElement).toBe(trigger)
    wrapper.unmount()
  })

  it.each([
    ['local', '无法播放此本地文件。请确认浏览器支持其编码，或替换为其他音频文件。'],
    ['sample', '无法播放歌曲录音。请保持 audio 文件夹与 works.html 的相对位置，并确认浏览器支持 MP3、WAV、M4A、MP4 音轨或 FLAC。'],
  ] as const)('shows the prototype play rejection message for %s audio', async (kind, message) => {
    vi.spyOn(HTMLMediaElement.prototype, 'play').mockRejectedValue(new Error('not supported'))
    const wrapper = mount(ClAudioPlayer, { props: { track: localTrack({ kind }) } })
    await flushPromises()

    expect(wrapper.find('.player-error').text()).toBe(message)
    expect(wrapper.find('.player-error').attributes('hidden')).toBeUndefined()
    expect(wrapper.find('.player-error').attributes('role')).toBe('status')
    expect(wrapper.find('.player-error').attributes('aria-live')).toBe('polite')
  })

  it.each([
    ['local', '浏览器无法解码此本地文件，请替换为支持的音频格式或编码。'],
    ['sample', '浏览器无法读取开放示例，请确认 audio 文件夹完整且与 works.html 放在一起。'],
  ] as const)('shows the prototype media error message for %s audio', async (kind, message) => {
    const wrapper = mount(ClAudioPlayer, { props: { track: localTrack({ kind }) } })
    await flushPromises()
    await wrapper.find('audio').trigger('error')

    expect(wrapper.find('.player-error').text()).toBe(message)
    expect(wrapper.find('.player-error').attributes('hidden')).toBeUndefined()
  })

  it('ignores a stale play rejection after the player has closed', async () => {
    let rejectPlay: ((reason: Error) => void) | undefined
    vi.spyOn(HTMLMediaElement.prototype, 'play').mockImplementation(() => new Promise<void>((_resolve, reject) => {
      rejectPlay = reject
    }))
    const wrapper = mount(ClAudioPlayer, { props: { track: localTrack({ kind: 'local' }) } })
    await flushPromises()
    await wrapper.find('.player-close').trigger('click')

    rejectPlay?.(new Error('late rejection'))
    await flushPromises()

    expect(wrapper.find('.player-error').text()).toBe('')
    expect(wrapper.find('aside').attributes('hidden')).not.toBeUndefined()
  })

  it('revokes a local object URL on close and on unmount', async () => {
    const createDescriptor = Object.getOwnPropertyDescriptor(URL, 'createObjectURL')
    const revokeDescriptor = Object.getOwnPropertyDescriptor(URL, 'revokeObjectURL')
    const createObjectURL = vi.fn(() => 'blob:local-recording')
    const revokeObjectURL = vi.fn()
    Object.defineProperty(URL, 'createObjectURL', { configurable: true, value: createObjectURL })
    Object.defineProperty(URL, 'revokeObjectURL', { configurable: true, value: revokeObjectURL })

    try {
      const blob = new Blob(['recording'], { type: 'audio/mpeg' })
      const wrapper = mount(ClAudioPlayer, {
        props: { track: localTrack({ kind: 'local', source: blob }) },
      })
      await flushPromises()
      expect(createObjectURL).toHaveBeenCalledWith(blob)
      expect(wrapper.find('audio').attributes('src')).toBe('blob:local-recording')

      await wrapper.find('.player-close').trigger('click')
      expect(revokeObjectURL).toHaveBeenCalledWith('blob:local-recording')

      await wrapper.setProps({ track: localTrack({ kind: 'local', source: blob }) })
      await flushPromises()
      wrapper.unmount()
      expect(revokeObjectURL).toHaveBeenCalledTimes(2)
      expect(document.body.classList.contains('audio-player-open')).toBe(false)
    } finally {
      if (createDescriptor) Object.defineProperty(URL, 'createObjectURL', createDescriptor)
      else Reflect.deleteProperty(URL, 'createObjectURL')
      if (revokeDescriptor) Object.defineProperty(URL, 'revokeObjectURL', revokeDescriptor)
      else Reflect.deleteProperty(URL, 'revokeObjectURL')
    }
  })

  it('emits playlist navigation and advances when the current recording ends', async () => {
    const wrapper = mount(ClAudioPlayer, {
      props: { track: localTrack(), playlistPosition: 1, playlistLength: 2 },
    })
    await flushPromises()

    expect(wrapper.find('.playlist-status').text()).toBe('循环列表 · 1 / 2')
    expect(wrapper.find('audio').attributes('loop')).toBeUndefined()
    await wrapper.find('[aria-label="播放列表上一首"]').trigger('click')
    expect(wrapper.emitted('previous')).toHaveLength(1)
    await wrapper.find('[aria-label="播放列表下一首"]').trigger('click')
    expect(wrapper.emitted('next')).toHaveLength(1)

    await wrapper.find('audio').trigger('ended')
    expect(wrapper.emitted('next')).toHaveLength(2)
  })

  it('does not turn a single recording into a playlist or auto-advance it', async () => {
    const wrapper = mount(ClAudioPlayer, { props: { track: localTrack() } })
    await flushPromises()

    expect(wrapper.find('.playlist-controls').exists()).toBe(false)
    await wrapper.find('audio').trigger('ended')
    expect(wrapper.emitted('next')).toBeUndefined()
  })
})
