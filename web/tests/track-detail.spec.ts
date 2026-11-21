import { flushPromises } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { mountAudioWorks, resetSharedPlayer } from './audio-works-harness'

describe('track detail integration', () => {
  beforeEach(() => {
    vi.spyOn(HTMLMediaElement.prototype, 'play').mockResolvedValue()
    vi.spyOn(HTMLMediaElement.prototype, 'pause').mockImplementation(() => {})
    vi.spyOn(HTMLMediaElement.prototype, 'load').mockImplementation(() => {})
  })

  afterEach(() => {
    resetSharedPlayer()
    document.body.classList.remove('audio-player-open', 'dialog-open')
    document.body.innerHTML = ''
  })

  it('opens complete metadata, cover, lyrics, score, source and rights for CN-C01', async () => {
    const wrapper = mountAudioWorks(true)
    await wrapper.find('[data-work-detail="CN-C01"]').trigger('click')
    await flushPromises()

    const dialog = wrapper.find('dialog.track-dialog')
    expect(dialog.attributes('open')).not.toBeUndefined()
    expect(dialog.find('#dialog-title').text()).toBe('让我们荡起双桨')
    expect(dialog.find('.dialog-meta').text()).toContain('CN-C01')
    expect(dialog.find('.dialog-meta').text()).toContain('约 2 分 12 秒')
    expect(dialog.find('.dialog-meta').text()).toContain('f362616eb1cca71ab438fbdb739b3dcc2d159f9eef35dce7a8b873fdb48c7f75')
    expect(dialog.find('.song-cover img').attributes('src')).toBe('/song-assets/CN-C01-cover.svg')
    expect(dialog.findAll('.lyrics-lines p')).toHaveLength(18)
    expect(dialog.find('.score-scroll img').attributes('src')).toBe('/song-assets/CN-C01-score.svg')
    expect(dialog.find('.score-downloads a[download]').exists()).toBe(true)
    expect(dialog.find('.sample-links a').attributes('href')).toContain('https://hsjd.jxust.edu.cn/')
    expect(dialog.find('#dialog-rights').text()).toContain('不得据此公开发布')
    expect(document.body.classList.contains('dialog-open')).toBe(true)

    await dialog.find('.sample-audio-panel button').trigger('click')
    await flushPromises()
    expect(wrapper.find('.player-title').text()).toBe('让我们荡起双桨')
    expect(wrapper.find('audio').attributes('src')).toBe('/audio/CN-C01-original.mp3')

    await dialog.find('.dialog-close').trigger('click')
    await flushPromises()
    expect(wrapper.find('dialog.track-dialog').exists()).toBe(false)
    expect(document.body.classList.contains('dialog-open')).toBe(false)
    expect(wrapper.find('.audio-player').attributes('hidden')).toBeUndefined()
    wrapper.unmount()
  })

  it('switches CN-C02 versions and stops the old version before playing the new one', async () => {
    const wrapper = mountAudioWorks(true)
    await wrapper.find('[data-work-detail="CN-C02"]').trigger('click')
    await flushPromises()

    const select = wrapper.find('#sample-version')
    expect(select.findAll('option')).toHaveLength(2)
    await wrapper.find('.sample-audio-panel button').trigger('click')
    await flushPromises()
    expect(wrapper.find('audio').attributes('src')).toBe('/audio/CN-C02-gxzf.flac')

    await select.setValue('1')
    await flushPromises()
    expect(wrapper.find('.sample-audio-panel').text()).toContain('学习强国视频原声版')
    expect(wrapper.find('.audio-player').attributes('hidden')).not.toBeUndefined()

    await wrapper.find('.sample-audio-panel button').trigger('click')
    await flushPromises()
    expect(wrapper.find('audio').attributes('src')).toBe('/audio/CN-C02-xuexi-chorus.m4a')
    expect(wrapper.find('.player-file').text()).toContain('公开视频原声音轨 · 童声合唱')
    wrapper.unmount()
  })

  it('keeps generated-audio disclosure and closes with Escape/cancel', async () => {
    const wrapper = mountAudioWorks(true)
    await wrapper.find('input[type="search"]').setValue('CN-C22')
    await wrapper.find('[data-work-detail="CN-C22"]').trigger('click')
    await flushPromises()

    expect(wrapper.find('#sample-audio-title').text()).toBe('原创播放示范 · 非原曲')
    expect(wrapper.find('#dialog-rights').text()).toContain('不是本曲旋律或歌曲录音')
    expect(wrapper.find('#dialog-rights').text()).toContain('CC0 许可仅覆盖该新音频')

    await wrapper.find('dialog.track-dialog').trigger('cancel')
    await flushPromises()
    expect(wrapper.find('dialog.track-dialog').exists()).toBe(false)
    expect(document.body.classList.contains('dialog-open')).toBe(false)
    wrapper.unmount()
  })
})
