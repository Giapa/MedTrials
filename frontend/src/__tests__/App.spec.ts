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
          eligibility: {
            criteria:
              'Inclusion Criteria:\n\n* Must be an adult.\n\nExclusion Criteria:\n\n* Prior condition.',
            minimum_age: '18 Years',
            maximum_age: null,
            sex: 'ALL',
            healthy_volunteers: false,
            gender_based: null,
            gender_description: null,
          },
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
    expect(wrapper.text()).toContain('Inclusion Criteria:')
    expect(wrapper.text()).toContain('Exclusion Criteria:')
    expect(wrapper.text()).toContain('18 Years')
    expect(wrapper.text()).toContain('Δεν αναφέρεται')
    const facts = wrapper.findAll('.participation-facts > div')
    const volunteers = facts.find((fact) => fact.text().includes('Δέχεται υγιείς εθελοντές'))
    expect(volunteers?.text()).toContain('Όχι')
    expect(wrapper.find('.participation a').attributes('href')).toBe(
      'https://clinicaltrials.gov/study/NCT02798055',
    )
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

describe('study search', () => {
  it('searches and shows a Greek location with its own status', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string) => {
        if (url === '/api/example-study') return { ok: false }
        return {
          ok: true,
          json: async () => ({
            studies: [
              {
                id: 'NCT12345678',
                title: 'Example search result',
                summary: null,
                eligibility: {
                  criteria: null,
                  minimum_age: null,
                  maximum_age: null,
                  sex: null,
                  healthy_volunteers: null,
                  gender_based: null,
                  gender_description: null,
                },
                status: 'RECRUITING',
                last_updated: null,
                locations: [
                  { facility: 'Athens Hospital', city: 'Athens', status: 'NOT_YET_RECRUITING' },
                ],
                source_url: 'https://clinicaltrials.gov/study/NCT12345678',
              },
            ],
            more_results: true,
            next_page_token: 'page-2',
          }),
        }
      }),
    )
    const wrapper = mount(App)
    await flushPromises()
    await wrapper.get('input[name="condition"]').setValue('breast cancer')
    await wrapper.get('input[name="openStudiesOnly"]').setValue(true)
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(fetch).toHaveBeenCalledWith(
      '/api/studies/search',
      expect.objectContaining({
        body: JSON.stringify({ condition: 'breast cancer', open_studies_only: true }),
      }),
    )
    expect(wrapper.text()).toContain('Example search result')
    expect(wrapper.text()).toContain('Athens Hospital')
    expect(wrapper.text()).toContain('Δεν έχει ξεκινήσει η προσέλκυση')
    expect(wrapper.text()).toContain('Υπάρχουν περισσότερα αποτελέσματα')
    expect(wrapper.text()).toContain('Το μητρώο δεν παρέχει κείμενο κριτηρίων.')
  })

  it('loads more for the submitted search even if the form changes', async () => {
    const study = (id: string, title: string) => ({
      id, title, summary: null, status: 'RECRUITING', last_updated: null,
      eligibility: { criteria: null, minimum_age: null, maximum_age: null, sex: null,
        healthy_volunteers: null, gender_based: null, gender_description: null },
      locations: [{ facility: 'Athens', city: 'Athens', status: null }],
      source_url: `https://clinicaltrials.gov/study/${id}`,
    })
    const fetchMock = vi.fn(async (url: string, options?: RequestInit) => {
      if (url === '/api/example-study') return { ok: false }
      const body = JSON.parse(String(options?.body))
      if (!body.page_token) return { ok: true, json: async () => ({
        studies: [study('NCT12345678', 'First study')], more_results: true, next_page_token: 'page-2',
      }) }
      return { ok: true, json: async () => ({
        studies: [study('NCT12345678', 'First study'), study('NCT87654321', 'Second study')],
        more_results: false, next_page_token: null,
      }) }
    })
    vi.stubGlobal('fetch', fetchMock)
    const wrapper = mount(App)
    await flushPromises()
    await wrapper.get('input[name="condition"]').setValue('breast cancer')
    await wrapper.get('input[name="openStudiesOnly"]').setValue(true)
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    await wrapper.get('input[name="condition"]').setValue('diabetes')
    await wrapper.get('input[name="openStudiesOnly"]').setValue(false)
    await wrapper.get('button[name="load-more"]').trigger('click')
    await flushPromises()
    expect(fetchMock).toHaveBeenCalledWith('/api/studies/search', expect.objectContaining({
      body: JSON.stringify({ condition: 'breast cancer', open_studies_only: true, page_token: 'page-2' }),
    }))
    expect(wrapper.findAll('.search-results article')).toHaveLength(2)
    expect(wrapper.text()).toContain('Second study')
    expect(wrapper.find('button[name="load-more"]').exists()).toBe(false)
  })
})
