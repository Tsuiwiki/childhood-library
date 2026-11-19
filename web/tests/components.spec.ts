import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import ClCard from '../src/components/ClCard.vue'
import ClFilterBar from '../src/components/ClFilterBar.vue'
import ClDetailDialog from '../src/components/ClDetailDialog.vue'

describe('ClCard', () => {
  it('renders title, kicker, badge, tone and the default slot', () => {
    const wrapper = mount(ClCard, {
      props: { title: '音乐馆', kicker: '01', tone: 'red', badge: '规划中' },
      slots: { default: '中国经典儿歌' },
    })

    expect(wrapper.find('.cl-card__title').text()).toBe('音乐馆')
    expect(wrapper.find('.cl-card__kicker').text()).toBe('01')
    expect(wrapper.find('.cl-card__badge').text()).toBe('规划中')
    expect(wrapper.find('.cl-card__body').text()).toBe('中国经典儿歌')
    expect(wrapper.classes()).toContain('cl-card--red')
    expect(wrapper.find('.cl-card__footer').exists()).toBe(false)
  })

  it('renders the footer slot only when provided', () => {
    const wrapper = mount(ClCard, {
      props: { title: '故事馆' },
      slots: { footer: '了解更多' },
    })
    expect(wrapper.find('.cl-card__footer').text()).toBe('了解更多')
  })
})

describe('ClFilterBar', () => {
  const filters = [
    { value: 'all', label: '全部' },
    { value: 'music', label: '音乐馆' },
  ]

  it('emits query changes and chip selection', async () => {
    const wrapper = mount(ClFilterBar, { props: { modelValue: '', filters, active: 'all' } })

    await wrapper.find('input[type="search"]').setValue('小燕子')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['小燕子'])

    await wrapper.findAll('.cl-filter__chip')[1]!.trigger('click')
    expect(wrapper.emitted('update:active')?.[0]).toEqual(['music'])
    expect(wrapper.findAll('.cl-filter__chip')[0]!.attributes('aria-pressed')).toBe('true')
  })

  it('resets query, active filter and emits reset', async () => {
    const wrapper = mount(ClFilterBar, { props: { modelValue: '李白', filters, active: 'music' } })
    await wrapper.find('.cl-filter__reset').trigger('click')

    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([''])
    expect(wrapper.emitted('update:active')?.[0]).toEqual(['all'])
    expect(wrapper.emitted('reset')).toHaveLength(1)
  })
})

describe('ClDetailDialog', () => {
  it('opens with the open attribute and closes on the Escape/cancel event', async () => {
    const wrapper = mount(ClDetailDialog, {
      props: { open: true, title: '设计边界' },
      slots: { default: '不导入业务数据' },
      attachTo: document.body,
    })

    const dialog = wrapper.find('dialog')
    expect(dialog.attributes('open')).not.toBeUndefined()
    expect(wrapper.text()).toContain('不导入业务数据')

    await dialog.trigger('cancel')
    expect(wrapper.emitted('close')).toHaveLength(1)

    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('close')).toHaveLength(2)
    wrapper.unmount()
  })

  it('stays closed when open is false', () => {
    const wrapper = mount(ClDetailDialog, { props: { open: false, title: '边界' } })
    expect(wrapper.find('dialog').attributes('open')).toBeUndefined()
  })
})
