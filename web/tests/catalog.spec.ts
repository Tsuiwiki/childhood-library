import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory } from 'vue-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import CatalogView from '../src/views/CatalogView.vue'
import {
  catalogAudioLinks,
  catalogAvailability,
  catalogDocumentUrl,
  catalogEntries,
  catalogLineUrl,
  catalogRecordings,
  catalogStats,
} from '../src/research/catalog'
import { createAppRouter } from '../src/router'

beforeEach(() => {
  vi.spyOn(window, 'scrollTo').mockImplementation(() => {})
})

async function mountCatalog(path = '/music/catalog') {
  const router = createAppRouter(createMemoryHistory())
  await router.push(path)
  await router.isReady()
  return mount(CatalogView, { global: { plugins: [router] } })
}

describe('structured 500-song bibliography catalogue', () => {
  it('keeps all 219 published rows with verifiable source line numbers', () => {
    expect(catalogEntries).toHaveLength(219)
    expect(catalogStats.v1).toBe(139)
    expect(catalogStats.v4).toBe(80)
    expect(new Set(catalogEntries.map((entry) => entry.id)).size).toBe(219)
    expect(catalogEntries.every((entry) => entry.status === 'bibliography_verified' && entry.review === '待评审')).toBe(true)
    expect(catalogEntries[0]).toMatchObject({ id: 'V1-001', title: '小老鼠上灯台', volume: 'V1', sourceLine: 47 })
    expect(catalogEntries[138]).toMatchObject({ id: 'V1-139', volume: 'V1' })
    expect(catalogEntries[139]).toMatchObject({ id: 'V4-001', volume: 'V4', sourceLine: 193 })
    expect(catalogEntries[218]).toMatchObject({ id: 'V4-080', title: '奔跑吧蜗牛', sourceLine: 272 })
    expect(catalogDocumentUrl).toContain('CHINESE_CHILDRENS_SONGS_500_CATALOG.md')
    expect(catalogLineUrl(catalogEntries[0]!)).toBe(`${catalogDocumentUrl}#L47`)
  })

  it('derives availability from real recordings and source links, never inventing audio', () => {
    expect(catalogStats.withRecording).toBe(3)
    expect(catalogStats.withSource).toBe(6)
    expect(catalogStats.bibliographyOnly).toBe(210)
    const paddle = catalogEntries.find((entry) => entry.title === '丢手绢')!
    expect(catalogAvailability(paddle)).toBe('recording')
    expect(catalogRecordings(paddle).length).toBeGreaterThan(0)
    const rabbit = catalogEntries.find((entry) => entry.title === '小兔子乖乖')!
    expect(catalogAvailability(rabbit)).toBe('source')
    expect(catalogAudioLinks(rabbit).length).toBeGreaterThan(0)
    expect(catalogAvailability(catalogEntries[0]!)).toBe('bibliography')
  })

  it('renders the first twelve works, links source lines and never shows a fake player', async () => {
    window.history.replaceState({}, '', '/music/catalog')
    const wrapper = await mountCatalog()
    await flushPromises()

    expect(wrapper.find('h1').text()).toBe('百年儿歌目录')
    expect(wrapper.text()).toContain('219')
    expect(wrapper.findAll('.catalog-card')).toHaveLength(12)
    expect(wrapper.find('audio').exists()).toBe(false)
    expect(wrapper.find('.catalog-count').text()).toContain('第 1 / 19 页')
    const first = wrapper.find('[data-catalog-id="V1-001"]')
    expect(first.text()).toContain('仅目录登记')
    expect(first.text()).toContain('暂无可听版本')
    expect(first.find('.catalog-source').attributes('href')).toBe(`${catalogDocumentUrl}#L47`)
  })

  it('gives real actions only where recordings or source links exist', async () => {
    window.history.replaceState({}, '', '/music/catalog?q=丢手绢')
    const wrapper = await mountCatalog('/music/catalog?q=丢手绢')
    await flushPromises()
    const card = wrapper.find('.catalog-card')
    expect(card.text()).toContain('已有')
    expect(card.find('.catalog-primary').attributes('href')).toMatch(/^\/works\?work=CN-/)

    window.history.replaceState({}, '', '/music/catalog?q=小兔子乖乖')
    const rabbit = await mountCatalog('/music/catalog?q=小兔子乖乖')
    await flushPromises()
    expect(rabbit.find('.catalog-primary').attributes('href')).toContain('/music/sources?q=')
  })

  it('combines search, volume filter, availability filter, pagination and empty-state recovery', async () => {
    window.history.replaceState({}, '', '/music/catalog')
    const wrapper = await mountCatalog()
    await flushPromises()
    const search = wrapper.find('input[type="search"]')

    await wrapper.findAll('.catalog-kinds')[0]!.findAll('button')[1]!.trigger('click')
    expect(wrapper.find('.catalog-count').text()).toContain('找到 139 首')

    await wrapper.findAll('.catalog-kinds')[0]!.findAll('button')[2]!.trigger('click')
    expect(wrapper.find('.catalog-count').text()).toContain('找到 80 首')

    await wrapper.findAll('.catalog-kinds')[0]!.findAll('button')[0]!.trigger('click')
    await wrapper.findAll('.catalog-states button')[1]!.trigger('click')
    expect(wrapper.find('.catalog-count').text()).toContain('找到 3 首')
    expect(wrapper.findAll('.catalog-card')).toHaveLength(3)

    await wrapper.findAll('.catalog-states button')[0]!.trigger('click')
    await search.setValue('送别')
    expect(wrapper.findAll('.catalog-card')).toHaveLength(1)
    expect(wrapper.find('.catalog-card h2').text()).toBe('送别')

    await search.setValue('不存在的歌')
    expect(wrapper.find('.catalog-empty').exists()).toBe(true)
    await wrapper.find('.catalog-empty button').trigger('click')
    expect(wrapper.findAll('.catalog-card')).toHaveLength(12)
    await wrapper.find('[aria-label="目录第 2 页"]').trigger('click')
    expect(wrapper.find('.catalog-count').text()).toContain('第 2 / 19 页')
  })
})
