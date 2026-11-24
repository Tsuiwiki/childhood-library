import { flushPromises, mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import AudioSourcesView from '../src/views/AudioSourcesView.vue'
import {
  audioLinksForWork,
  audioSourceLinks,
  sampleForAudioLink,
} from '../src/research/audioLinks'

function mountSources() {
  return mount(AudioSourcesView, {
    global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
  })
}

describe('collected audio source links', () => {
  it('keeps 136 curated GitHub entries with unique IDs and safe external URLs', () => {
    expect(audioSourceLinks).toHaveLength(136)
    expect(new Set(audioSourceLinks.map((link) => link.id)).size).toBe(136)
    expect(audioSourceLinks.every((link) => new URL(link.url).protocol === 'https:')).toBe(true)
    expect(audioLinksForWork('CN-C01')).toHaveLength(12)
    expect(audioLinksForWork('CN-C02')).toHaveLength(10)
    expect(sampleForAudioLink(audioSourceLinks.find((link) => link.id === '06-01')!)).toBeUndefined()
    expect(sampleForAudioLink(audioSourceLinks.find((link) => link.id === '05-01')!)?.id).toBe('CN-C06')
  })

  it('includes batch 13 album entrances and work-level clues without claiming downloads', () => {
    const batch13 = audioSourceLinks.filter((link) => link.batch === '13')
    expect(batch13).toHaveLength(14)
    expect(batch13.map((link) => link.id)).toContain('13-01')
    expect(batch13.map((link) => link.id)).toContain('13-14')
    expect(batch13.every((link) => link.kind === 'album' || link.kind === 'archive')).toBe(true)
    expect(batch13.some((link) => link.note.includes('专辑内逐曲试听'))).toBe(true)
    expect(audioSourceLinks.some((link) => link.id === '04A-01')).toBe(true)
    expect(audioSourceLinks.some((link) => link.url.includes('gequbao.com'))).toBe(false)
  })

  it('indexes research batches 14-23 with traceable notes and https-only links', () => {
    const later = audioSourceLinks.filter((link) => Number(link.batch) >= 14)
    expect(later).toHaveLength(42)
    expect(new Set(later.map((link) => link.batch)).size).toBe(6)
    expect(later.every((link) => link.note.includes('批次') && link.url.startsWith('https://'))).toBe(true)
    expect(new Set(later.map((link) => link.url)).size).toBe(later.length)
  })

  it('renders the first twelve source records without inventing local audio', async () => {
    window.history.replaceState({}, '', '/music/sources')
    const wrapper = mountSources()
    await flushPromises()

    expect(wrapper.find('h1').text()).toBe('儿歌音源链接')
    expect(wrapper.text()).toContain('共 136 条')
    expect(wrapper.findAll('.source-card')).toHaveLength(12)
    expect(wrapper.find('audio').exists()).toBe(false)
    expect(wrapper.find('[data-source-id="05-01"] .source-primary').attributes('href')).toContain('music.apple.com')
    expect(wrapper.find('[data-source-id="05-01"]').text()).toContain('查看已有研究录音')
    expect(wrapper.find('.source-count').text()).toContain('第 1 / 12 页')
  })

  it('finds link-only works and keeps their original platform entrance', async () => {
    window.history.replaceState({}, '', '/music/sources?q=小白船')
    const wrapper = mountSources()
    await flushPromises()

    const cards = wrapper.findAll('.source-card')
    expect(cards).toHaveLength(2)
    expect(cards[0].text()).toContain('北京蓝天艺术合唱小组')
    expect(cards[0].text()).toContain('仅外部入口 · 未采集本地音频')
    expect(cards[0].text()).not.toContain('查看已有研究录音')
    expect(cards[1].find('.source-primary').attributes('href')).toBe('https://www.youtube.com/watch?v=oSV1-zVXVyI')
  })

  it('combines search, kind filters, recovery and pagination', async () => {
    window.history.replaceState({}, '', '/music/sources')
    const wrapper = mountSources()
    await flushPromises()
    const search = wrapper.find('input[type="search"]')

    await search.setValue('让我们荡起双桨')
    const cards = wrapper.findAll('.source-card')
    expect(cards).toHaveLength(12)
    expect(cards.slice(0, 3).every((card) => card.text().includes('查看已有研究录音'))).toBe(true)
    expect(cards.some((card) => card.text().includes('中国电影百年歌曲精萃（三）'))).toBe(true)

    await search.setValue('')
    const video = wrapper.findAll('.source-kinds button').find((button) => button.text() === '视频演绎')
    await video?.trigger('click')
    expect(wrapper.findAll('.source-card')).toHaveLength(11)
    expect(wrapper.find('.source-count').text()).toContain('找到 11 条')

    await search.setValue('not-a-source')
    expect(wrapper.find('.source-empty').exists()).toBe(true)
    await wrapper.find('.source-empty button').trigger('click')
    expect(wrapper.findAll('.source-card')).toHaveLength(12)
    await wrapper.find('[aria-label="音源第 2 页"]').trigger('click')
    expect(wrapper.find('.source-count').text()).toContain('第 2 / 12 页')
    expect(wrapper.find('[data-source-id="05-13"]').exists()).toBe(true)
  })
})
