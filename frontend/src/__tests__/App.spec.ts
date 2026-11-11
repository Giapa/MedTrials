import { mount, flushPromises } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from '../App.vue'

afterEach(() => vi.unstubAllGlobals())

describe('example study', () => {
  it('shows a registry record, its status, and a source link', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          id: 'NCT02798055',
          title: 'A registry study',
          summary: 'Study summary',
          status: 'COMPLETED',
          last_updated: '2019-07-05',
          locations: [{ facility: 'Athens Hospital', city: 'Athens' }],
          source_url: 'https://clinicaltrials.gov/study/NCT02798055',
        }),
      }),
    )
    const wrapper = mount(App)
    await flushPromises()
    expect(wrapper.text()).toContain('A registry study')
    expect(wrapper.text()).toContain('Ολοκληρωμένη')
    expect(wrapper.find('a[href="https://clinicaltrials.gov/study/NCT02798055"]').exists()).toBe(
      true,
    )
    await wrapper.get('button[aria-pressed="false"]').trigger('click')
    expect(wrapper.text()).toContain('Completed')
  })

  it('shows an error instead of a trial when the source fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')))
    const wrapper = mount(App)
    await flushPromises()
    expect(wrapper.get('[role="alert"]').text()).toContain('Δεν ήταν δυνατή')
    expect(wrapper.find('article').exists()).toBe(false)
  })
})
