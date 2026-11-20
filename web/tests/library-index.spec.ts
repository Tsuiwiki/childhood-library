import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory } from 'vue-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import LibraryIndexView from '../src/views/LibraryIndexView.vue'
import ResearchHallView from '../src/views/ResearchHallView.vue'
import WorksView from '../src/views/WorksView.vue'
import { documentUrl, documentsForWork } from '../src/research/documents'
import { specialtyCatalog, workSpecialties } from '../src/research/specialties'
import { createAppRouter } from '../src/router'

beforeEach(() => {
  vi.spyOn(window, 'scrollTo').mockImplementation(() => {})
  vi.spyOn(HTMLMediaElement.prototype, 'play').mockResolvedValue()
  vi.spyOn(HTMLMediaElement.prototype, 'pause').mockImplementation(() => {})
  vi.spyOn(HTMLMediaElement.prototype, 'load').mockImplementation(() => {})
})
afterEach(() => {
  vi.restoreAllMocks()
  document.body.classList.remove('dialog-open', 'audio-player-open')
  document.body.innerHTML = ''
})

async function routerAt(path: string) {
  const router = createAppRouter(createMemoryHistory())
  await router.push(path)
  await router.isReady()
  return router
}

describe('connected library research', () => {
  it('links existing work identities to specialties and research documents without copying records', async () => {
    expect(specialtyCatalog).toHaveLength(105)
    expect(workSpecialties('CN-C03').map((item) => item.id)).toEqual(['childhood', 'nature'])
    const documents = documentsForWork('CN-C03')
    expect(documents.map((item) => item.id)).toEqual(['songs-history-02', 'songs-research-02'])
    expect(documentUrl(documents[0]!.path)).toContain('github.com/Tsuiwiki/childhood-library/blob/main/docs/')

    const router = await routerAt('/library')
    const wrapper = mount(LibraryIndexView, { global: { plugins: [router] } })
    expect(wrapper.findAll('.hall-card')).toHaveLength(3)
    expect(wrapper.findAll('.document-card')).toHaveLength(6)
    expect(wrapper.find('.result-list').exists()).toBe(false)

    await wrapper.find('#library-query').setValue('小燕子')
    expect(wrapper.findAll('.result-card')).toHaveLength(3)
    expect(wrapper.find('.result-card a').attributes('href')).toBe('/works?work=CN-C03')
    expect(wrapper.text()).toContain('批次 02')
  })

  it('combines cross-hall search, type filters and empty-state recovery', async () => {
    const router = await routerAt('/library')
    const wrapper = mount(LibraryIndexView, { global: { plugins: [router] } })

    await wrapper.find('#library-query').setValue('女娲补天')
    expect(wrapper.find('.result-card h4').text()).toBe('女娲补天')
    expect(wrapper.find('.result-card a').attributes('href')).toBe('/story?q=ST-001')

    await wrapper.find('#library-query').setValue('批次 04')
    expect(wrapper.findAll('.result-card.is-document')).toHaveLength(2)
    const storyFilter = wrapper.findAll('.filters button').find((button) => button.text() === '故事')!
    await storyFilter.trigger('click')
    expect(wrapper.find('.empty').exists()).toBe(true)
    await wrapper.find('.empty button').trigger('click')
    expect(wrapper.find('.result-list').exists()).toBe(false)
    expect(wrapper.find('#library-query').element).toHaveProperty('value', '')
  })

  it('opens a specific story record from the library search link', async () => {
    const router = await routerAt('/story?q=ST-001')
    const wrapper = mount(ResearchHallView, { props: { hall: 'story' }, global: { plugins: [router] } })
    await flushPromises()
    expect(wrapper.find('input[type="search"]').element).toHaveProperty('value', 'ST-001')
    expect(wrapper.findAll('.rec-card')).toHaveLength(1)
    expect(wrapper.find('.rec-card h3').text()).toBe('女娲补天')
  })

  it('surfaces specialty and research-document links inside a recording detail', async () => {
    const router = await routerAt('/works')
    const wrapper = mount(WorksView, { attachTo: document.body, global: { plugins: [router] } })
    await wrapper.find('[data-work-detail="CN-C03"]').trigger('click')
    await flushPromises()

    expect(wrapper.find('.work-context').text()).toContain('作品脉络')
    expect(wrapper.find('.work-context').text()).toContain('童年的歌')
    expect(wrapper.find('.work-context').text()).toContain('大自然的歌')
    expect(wrapper.find('.work-context').text()).toContain('逐曲研究档案 · 批次 02')
    expect(wrapper.find('.work-context a[href*="CHINESE_CHILDRENS_SONGS_BATCH_02.md"]').exists()).toBe(true)
    wrapper.unmount()
    document.body.innerHTML = ''
  })
})
