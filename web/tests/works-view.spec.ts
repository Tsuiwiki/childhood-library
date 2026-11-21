import { flushPromises } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import sampleRecords from '../../design-demos/audio/samples.json'
import { mountAudioWorks as mountWorks, resetSharedPlayer } from './audio-works-harness'

describe('WorksView audio integration', () => {
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
    ['CN-C22', '播放原创示范', '原创播放示范 · 非原曲', '/audio/CN-C22.wav'],
    ['CN-C25', '试听歌曲示例', '开放许可 / 原创示范', '/audio/CN-C25.wav'],
    ['EN-T01', '试听歌曲示例', 'CC BY-SA 3.0', '/audio/EN-T01.mp3'],
  ])('keeps the recording-specific action and rights label for %s', async (id, action, label, source) => {
    const wrapper = mountWorks()
    await wrapper.find('input[type="search"]').setValue(id)
    const button = wrapper.find(`[data-work-id="${id}"]`)
    expect(button.text()).toBe(action)

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
})
