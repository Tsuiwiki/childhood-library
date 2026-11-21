import { flushPromises } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import sampleRecords from '../../design-demos/audio/samples.json'
import { mountAudioWorks as mountWorks, resetSharedPlayer } from './audio-works-harness'

describe('WorksView audio integration', () => {
  beforeEach(() => {
    window.history.replaceState({}, '', '/works')
    vi.spyOn(HTMLMediaElement.prototype, 'play').mockResolvedValue()
    vi.spyOn(HTMLMediaElement.prototype, 'pause').mockImplementation(() => {})
    vi.spyOn(HTMLMediaElement.prototype, 'load').mockImplementation(() => {})
  })

  afterEach(() => {
    resetSharedPlayer()
    document.body.classList.remove('audio-player-open', 'dialog-open')
    document.body.innerHTML = ''
  })

  it('renders the first nine research recordings with detail and play buttons', () => {
    const wrapper = mountWorks()

    expect(wrapper.findAll('.work-card')).toHaveLength(9)
    expect(wrapper.findAll('[data-audio-play]')).toHaveLength(9)
    expect(wrapper.findAll('[data-work-detail]')).toHaveLength(9)
    expect(wrapper.find('h1').text()).toBe('曲目列表')
    expect(wrapper.text()).toContain('58 条主录音记录')
    expect(wrapper.text()).toContain('不是已发布曲库')
    expect(wrapper.find('[data-work-id="CN-C01"]').exists()).toBe(true)
    expect(wrapper.find('[data-work-id="CN-C10"]').exists()).toBe(false)
    expect(wrapper.find('.audio-player').attributes('hidden')).not.toBeUndefined()
    expect(sampleRecords).toHaveLength(58)
  })

  it('uses the same content-card language as the homepage without stamped rights badges', () => {
    const wrapper = mountWorks()
    const card = wrapper.find('.work-card')

    expect(card.find('.work-cover img').exists()).toBe(true)
    expect(card.find('.work-body h2').text()).toBe('让我们荡起双桨')
    expect(card.find('.work-credit').text()).toContain('中央人民')
    expect(card.find('.play-button').text()).toContain('试听')
    expect(card.find('.detail-link').text()).toContain('看详情')
    expect(wrapper.findAll('.status-badge')).toHaveLength(0)
    expect(wrapper.findAll('.id-tag')).toHaveLength(0)
    expect(wrapper.findAll('.card-meta')).toHaveLength(0)
    // Rights detail is still reachable, just not stamped on every card.
    expect(wrapper.find('.rights-note').exists()).toBe(true)
    expect(wrapper.text()).toContain('不是已发布曲库')
  })

  it('plays the selected card, switches recordings and closes back to the list', async () => {
    const play = vi.spyOn(HTMLMediaElement.prototype, 'play')
    const wrapper = mountWorks(true)
    const firstButton = wrapper.find('[data-work-id="CN-C01"]')

    await firstButton.trigger('click')
    await flushPromises()

    expect(wrapper.find('.audio-player').attributes('hidden')).toBeUndefined()
    expect(wrapper.find('.player-title').text()).toBe('让我们荡起双桨')
    expect(wrapper.find('.player-kicker').text()).toContain('内部经典录音 · 权利待核验')
    expect(wrapper.find('.player-file').text()).toContain('经典童声合唱（完整歌曲）')
    expect(wrapper.find('audio').attributes('src')).toBe('/audio/CN-C01-original.mp3')
    expect(play).toHaveBeenCalledTimes(1)

    await wrapper.find('[data-work-id="CN-C02"]').trigger('click')
    await flushPromises()
    expect(wrapper.find('.player-title').text()).toBe('我们的田野')
    expect(wrapper.find('audio').attributes('src')).toBe('/audio/CN-C02-gxzf.flac')
    expect(play).toHaveBeenCalledTimes(2)

    await wrapper.find('.player-close').trigger('click')
    await flushPromises()
    expect(wrapper.find('.audio-player').attributes('hidden')).not.toBeUndefined()
    expect(wrapper.find('audio').attributes('src')).toBeUndefined()
    expect(document.body.classList.contains('audio-player-open')).toBe(false)
    expect(document.activeElement?.getAttribute('data-work-id')).toBe('CN-C02')
    wrapper.unmount()
  })

  it.each([
    ['CN-C22', '原创播放示范 · 非原曲', '/audio/CN-C22.wav'],
    ['CN-C25', '开放许可 / 原创示范', '/audio/CN-C25.wav'],
    ['EN-T01', 'CC BY-SA 3.0', '/audio/EN-T01.mp3'],
  ])('plays the right recording and keeps its rights label in the player for %s', async (id, label, source) => {
    const wrapper = mountWorks()
    await wrapper.find('input[type="search"]').setValue(id)
    const button = wrapper.find(`[data-work-id="${id}"]`)
    expect(button.text()).toContain('试听')

    await button.trigger('click')
    await flushPromises()

    expect(wrapper.find('.player-kicker').text()).toContain(label)
    expect(wrapper.find('audio').attributes('src')).toBe(source)
    wrapper.unmount()
  })

  it('searches, filters by category and recovers from an empty result', async () => {
    const wrapper = mountWorks()
    const search = wrapper.find('input[type="search"]')

    await search.setValue('小燕子')
    expect(wrapper.findAll('.work-card')).toHaveLength(1)
    expect(wrapper.find('.work-card').text()).toContain('小燕子')

    await search.setValue('')
    const generated = wrapper.findAll('.category-filters button')
      .find((button) => button.text() === '原创示范 · 非原曲')
    await generated?.trigger('click')
    expect(wrapper.find('.results-status').text()).toContain('找到 21 条')
    expect(wrapper.findAll('.work-card')).toHaveLength(9)

    await search.setValue('not-a-recording')
    expect(wrapper.find('.no-results').exists()).toBe(true)
    await wrapper.find('.no-results button').trigger('click')
    expect(wrapper.find('.results-status').text()).toContain('找到 58 条')
    expect(wrapper.findAll('.work-card')).toHaveLength(9)
  })

  it('filters recordings by a linked music specialty and returns to the full list', async () => {
    window.history.replaceState({}, '', '/works?topic=nature')
    const wrapper = mountWorks()
    await flushPromises()

    expect(wrapper.find('h1').text()).toBe('大自然的歌 · 已有录音')
    expect(wrapper.find('.topic-context').text()).toContain('来自音乐专题')
    expect(wrapper.find('.results-status').text()).toContain('找到 19 条')
    expect(wrapper.findAll('.work-card')).toHaveLength(9)
    expect(wrapper.find('[data-work-id="CN-C03"]').exists()).toBe(true)

    await wrapper.find('.topic-context button').trigger('click')
    expect(wrapper.find('h1').text()).toBe('曲目列表')
    expect(wrapper.find('.topic-context').exists()).toBe(false)
    expect(wrapper.find('.results-status').text()).toContain('找到 58 条')
  })

  it('paginates without losing the selected audio', async () => {
    const wrapper = mountWorks()
    await wrapper.find('[data-work-id="CN-C01"]').trigger('click')
    await flushPromises()

    await wrapper.find('[aria-label="第 2 页"]').trigger('click')
    expect(wrapper.find('[data-work-id="CN-C10"]').exists()).toBe(true)
    expect(wrapper.find('[data-work-id="CN-C01"]').exists()).toBe(false)
    expect(wrapper.find('.results-status').text()).toContain('第 2 / 7 页')
    expect(wrapper.find('.player-title').text()).toBe('让我们荡起双桨')

    const next = wrapper.findAll('.pagination button').find((button) => button.text() === '下一页')
    await next?.trigger('click')
    expect(wrapper.find('.results-status').text()).toContain('第 3 / 7 页')
  })

  it('loops every filtered result, wraps at both ends and keeps the launch snapshot', async () => {
    const wrapper = mountWorks()
    const start = wrapper.find('[data-playlist-start]')
    expect(start.text()).toBe('循环播放当前 58 首')

    await start.trigger('click')
    await flushPromises()
    expect(wrapper.find('.player-title').text()).toBe('让我们荡起双桨')
    expect(wrapper.find('.playlist-status').text()).toBe('循环列表 · 1 / 58')

    await wrapper.find('[aria-label="播放列表上一首"]').trigger('click')
    await flushPromises()
    expect(wrapper.find('.playlist-status').text()).toBe('循环列表 · 58 / 58')
    await wrapper.find('[aria-label="播放列表下一首"]').trigger('click')
    await flushPromises()
    expect(wrapper.find('.playlist-status').text()).toBe('循环列表 · 1 / 58')

    await wrapper.find('[aria-label="播放列表下一首"]').trigger('click')
    await flushPromises()
    expect(wrapper.find('.player-title').text()).toBe('我们的田野')
    await wrapper.find('audio').trigger('ended')
    await flushPromises()
    expect(wrapper.find('.playlist-status').text()).toBe('循环列表 · 3 / 58')

    await wrapper.find('input[type="search"]').setValue('小燕子')
    expect(wrapper.find('[data-playlist-start]').text()).toBe('循环播放当前 1 首')
    expect(wrapper.find('.playlist-status').text()).toBe('循环列表 · 3 / 58')
    await wrapper.find('[data-playlist-start]').trigger('click')
    await flushPromises()
    expect(wrapper.find('.playlist-status').text()).toBe('循环列表 · 1 / 1')

    const play = vi.spyOn(HTMLMediaElement.prototype, 'play')
    const callsBeforeReplay = play.mock.calls.length
    await wrapper.find('audio').trigger('ended')
    await flushPromises()
    expect(wrapper.find('.playlist-status').text()).toBe('循环列表 · 1 / 1')
    expect(play).toHaveBeenCalledTimes(callsBeforeReplay + 1)

    await wrapper.find('.player-close').trigger('click')
    await flushPromises()
    expect(wrapper.find('.playlist-controls').exists()).toBe(false)
  })
})
