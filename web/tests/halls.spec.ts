import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory } from 'vue-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from '../src/App.vue'
import MusicView from '../src/views/MusicView.vue'
import ResearchHallView from '../src/views/ResearchHallView.vue'
import SpecialtyView from '../src/views/SpecialtyView.vue'
import WorksView from '../src/views/WorksView.vue'
import { createAppRouter } from '../src/router'
import { hallGroups, hallRecords, hallStats } from '../src/research/library'
import { specialtyCount, specialtyDefinitions, specialtyWorks } from '../src/research/specialties'

async function routerAt(path: string) {
  const router = createAppRouter(createMemoryHistory())
  await router.push(path)
  await router.isReady()
  return router
}

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
  window.history.replaceState({}, '', '/')
})

describe('museum research data', () => {
  it('keeps all 160 story and poetry records in their original groups', () => {
    expect(hallRecords('story')).toHaveLength(100)
    expect(hallRecords('poetry')).toHaveLength(60)
    expect(hallGroups('story')).toHaveLength(9)
    expect(hallGroups('poetry')).toHaveLength(10)
    expect(hallStats('story')).toEqual({ total: 100, groups: 9, works: 85, special: 15 })
    expect(hallStats('poetry')).toEqual({ total: 60, groups: 10, works: 48, special: 12 })
    expect(new Set([...hallRecords('story'), ...hallRecords('poetry')].map((record) => record.id)).size).toBe(160)
  })

  it('derives all eight music specialty counts from the existing work mappings', () => {
    expect(specialtyDefinitions).toHaveLength(8)
    expect(specialtyDefinitions.map((item) => specialtyCount(item.id))).toEqual([35, 24, 32, 13, 3, 51, 18, 0])
    expect(specialtyWorks('childhood')[0]?.id).toBe('CN-C01')
  })
})

describe('MusicView and specialties', () => {
  it('renders the eight topics, three pillars and research boundary', async () => {
    const router = await routerAt('/music')
    const wrapper = mount(MusicView, { global: { plugins: [router] } })

    expect(wrapper.find('h1').text()).toContain('以中国经典为根')
    expect(wrapper.findAll('.spec-card')).toHaveLength(8)
    expect(wrapper.find('.spec-card').attributes('href')).toBe('/music/specialties/childhood')
    expect(wrapper.findAll('.pillar-card')).toHaveLength(3)
    expect(wrapper.text()).toContain('105 条已登记')
    expect(wrapper.text()).toContain('58 条有录音的研究记录')
    expect(wrapper.find('.lib-music').attributes('aria-current')).toBe('page')
  })

  it('renders 35 childhood candidates and opens a research recording through the works route', async () => {
    const router = await routerAt('/music/specialties/childhood')
    const wrapper = mount(SpecialtyView, { global: { plugins: [router] } })

    expect(wrapper.find('h1').text()).toBe('童年的歌')
    expect(wrapper.findAll('.work-card')).toHaveLength(35)
    const first = wrapper.find('.work-card')
    expect(first.text()).toContain('让我们荡起双桨')
    expect(first.attributes('href')).toBe('/works?work=CN-C01')
    expect(wrapper.text()).toContain('查看研究录音')
    expect(wrapper.findAll('.lib-peer-list a')).toHaveLength(8)
  })

  it('shows the original-topic empty state and handles an unknown topic honestly', async () => {
    const originalRouter = await routerAt('/music/specialties/original')
    const original = mount(SpecialtyView, { global: { plugins: [originalRouter] } })
    expect(original.findAll('.work-card')).toHaveLength(0)
    expect(original.find('.empty').text()).toContain('当前暂无已登记曲目')
    expect(original.text()).toContain('可追溯授权')

    const missingRouter = await routerAt('/music/specialties/not-real')
    const missing = mount(SpecialtyView, { global: { plugins: [missingRouter] } })
    expect(missing.find('h1').text()).toBe('没有找到这个音乐专题')
    expect(missing.find('.works-grid').exists()).toBe(false)
  })
})

describe('story and poetry research halls', () => {
  it('renders 100 story records and combines keyword and group filters', async () => {
    const router = await routerAt('/story')
    const wrapper = mount(ResearchHallView, {
      props: { hall: 'story' },
      global: { plugins: [router] },
    })

    expect(wrapper.findAll('.rec-card')).toHaveLength(100)
    expect(wrapper.findAll('.group-section')).toHaveLength(9)
    expect(wrapper.find('.result-count').text()).toBe('显示 100 / 100 条')

    await wrapper.find('input[type="search"]').setValue('ST-001')
    expect(wrapper.findAll('.rec-card')).toHaveLength(1)
    expect(wrapper.find('.rec-card h3').text()).toBe('女娲补天')
    expect(wrapper.findAll('.group-section')).toHaveLength(1)

    await wrapper.find('select').setValue('original')
    expect(wrapper.find('.empty').exists()).toBe(true)
    await wrapper.find('.empty button').trigger('click')
    expect(wrapper.findAll('.rec-card')).toHaveLength(100)

    await wrapper.find('select').setValue('original')
    expect(wrapper.findAll('.rec-card')).toHaveLength(15)
    expect(wrapper.text()).toContain('征集方向')
  })

  it('renders 60 poetry records, filters asset groups and expands native research details', async () => {
    const router = await routerAt('/poetry')
    const wrapper = mount(ResearchHallView, {
      props: { hall: 'poetry' },
      global: { plugins: [router] },
    })

    expect(wrapper.findAll('.rec-card')).toHaveLength(60)
    expect(wrapper.findAll('.group-section')).toHaveLength(10)
    expect(wrapper.text()).not.toContain('**')

    await wrapper.find('select').setValue('music')
    expect(wrapper.findAll('.rec-card')).toHaveLength(6)
    expect(wrapper.find('.group-section h2').text()).toContain('诗词入乐')

    const details = wrapper.find('details')
    expect(details.attributes('open')).toBeUndefined()
    await wrapper.find('summary').trigger('click')
    expect(wrapper.find('details').attributes('open')).not.toBeUndefined()
    expect(wrapper.find('details').text()).toContain('资产边界')
    expect(wrapper.find('details a').attributes('href')).toBe('/music/specialties/classical')
  })
})

describe('museum navigation and recording deep links', () => {
  it('opens the mobile navigation and closes it after a route change', async () => {
    const router = await routerAt('/music')
    const wrapper = mount(App, { global: { plugins: [router] } })
    const toggle = wrapper.find('.menu-toggle')

    await toggle.trigger('click')
    expect(toggle.attributes('aria-expanded')).toBe('true')
    expect(wrapper.find('#mobile-nav').exists()).toBe(true)

    await router.push('/story')
    await flushPromises()
    expect(wrapper.find('#mobile-nav').exists()).toBe(false)
    expect(wrapper.find('.site-footer').exists()).toBe(false)
  })

  it('opens the requested recording detail when arriving from a specialty card', async () => {
    window.history.replaceState({}, '', '/works?work=CN-C02')
    const wrapper = mount(WorksView, { attachTo: document.body })
    await flushPromises()

    expect(wrapper.find('dialog').exists()).toBe(true)
    expect(wrapper.find('#dialog-title').text()).toBe('我们的田野')
    expect(wrapper.text()).toContain('CN-C02')
    wrapper.unmount()
  })
})
