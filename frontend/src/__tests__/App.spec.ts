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
      'https://clinicaltrials.gov/study/NCT02798055#participation-criteria',
    )
    expect(wrapper.get('.summary-source').attributes('href')).toBe(
      'https://clinicaltrials.gov/study/NCT02798055#study-overview',
    )
    expect(wrapper.get('.locations-source').attributes('href')).toBe(
      'https://clinicaltrials.gov/study/NCT02798055#contacts-and-locations',
    )
    expect(wrapper.get('.dates-source').attributes('href')).toBe(
      'https://clinicaltrials.gov/study/NCT02798055#study-record-dates',
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

  it('says when the example record is rate limited', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 429 }))
    const wrapper = mount(App)
    await flushPromises()
    expect(wrapper.get('.study-section [role="alert"]').text()).toContain(
      'Η σύνδεση με το μητρώο είναι απασχολημένη',
    )
  })
})

describe('study search', () => {
  it('says when a new search is rate limited', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string) =>
        url === '/api/example-study' ? { ok: false } : { ok: false, status: 429 },
      ),
    )
    const wrapper = mount(App)
    await flushPromises()
    await wrapper.get('input[name="condition"]').setValue('diabetes')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(wrapper.get('.search-section [role="alert"]').text()).toContain(
      'Η σύνδεση με το μητρώο είναι απασχολημένη',
    )
    expect(wrapper.find('.search-results').exists()).toBe(false)
  })

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
      id,
      title,
      summary: null,
      status: 'RECRUITING',
      last_updated: null,
      eligibility: {
        criteria: null,
        minimum_age: null,
        maximum_age: null,
        sex: null,
        healthy_volunteers: null,
        gender_based: null,
        gender_description: null,
      },
      locations: [{ facility: 'Athens', city: 'Athens', status: null }],
      source_url: `https://clinicaltrials.gov/study/${id}`,
    })
    let pageAttempts = 0
    const fetchMock = vi.fn(async (url: string, options?: RequestInit) => {
      if (url === '/api/example-study') return { ok: false }
      const body = JSON.parse(String(options?.body))
      if (!body.page_token)
        return {
          ok: true,
          json: async () => ({
            studies: [study('NCT12345678', 'First study')],
            more_results: true,
            next_page_token: 'page-2',
          }),
        }
      pageAttempts += 1
      if (pageAttempts === 1) return { ok: false, status: 429 }
      return {
        ok: true,
        json: async () => ({
          studies: [study('NCT12345678', 'First study'), study('NCT87654321', 'Second study')],
          more_results: false,
          next_page_token: null,
        }),
      }
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
    expect(wrapper.text()).toContain('First study')
    expect(wrapper.text()).toContain('Η σύνδεση με το μητρώο είναι απασχολημένη')
    expect(wrapper.text()).toContain('Τα προηγούμενα αποτελέσματα παραμένουν διαθέσιμα')
    await wrapper.get('button[name="load-more"]').trigger('click')
    await flushPromises()
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/studies/search',
      expect.objectContaining({
        body: JSON.stringify({
          condition: 'breast cancer',
          open_studies_only: true,
          page_token: 'page-2',
        }),
      }),
    )
    expect(wrapper.findAll('.search-results article')).toHaveLength(2)
    expect(wrapper.text()).toContain('Second study')
    expect(wrapper.find('button[name="load-more"]').exists()).toBe(false)
  })

  it('does not replace a new search with a late page from the old search', async () => {
    const study = (id: string, title: string) => ({
      id,
      title,
      summary: null,
      status: null,
      last_updated: null,
      eligibility: {
        criteria: null,
        minimum_age: null,
        maximum_age: null,
        sex: null,
        healthy_volunteers: null,
        gender_based: null,
        gender_description: null,
      },
      locations: [],
      source_url: `https://clinicaltrials.gov/study/${id}`,
    })
    let finishPage: (result: { ok: boolean; json: () => Promise<unknown> }) => void = () => {}
    const delayedPage = new Promise<{ ok: boolean; json: () => Promise<unknown> }>((resolve) => {
      finishPage = resolve
    })
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string, options?: RequestInit) => {
        if (url === '/api/example-study') return { ok: false }
        const body = JSON.parse(String(options?.body))
        if (body.page_token) return delayedPage
        if (body.condition === 'diabetes')
          return {
            ok: true,
            json: async () => ({
              studies: [study('NCT22222222', 'New search result')],
              more_results: false,
              next_page_token: null,
            }),
          }
        return {
          ok: true,
          json: async () => ({
            studies: [study('NCT11111111', 'Old search result')],
            more_results: true,
            next_page_token: 'next',
          }),
        }
      }),
    )
    const wrapper = mount(App)
    await flushPromises()
    await wrapper.get('input[name="condition"]').setValue('breast cancer')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    await wrapper.get('button[name="load-more"]').trigger('click')
    await wrapper.get('input[name="condition"]').setValue('diabetes')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    finishPage({
      ok: true,
      json: async () => ({
        studies: [study('NCT33333333', 'Late result')],
        more_results: false,
        next_page_token: null,
      }),
    })
    await flushPromises()
    expect(wrapper.text()).toContain('New search result')
    expect(wrapper.text()).not.toContain('Late result')
    expect(wrapper.text()).not.toContain('Old search result')
  })
})

describe('Greek search suggestions', () => {
  it('requires the user to choose a sourced suggestion before searching', async () => {
    const fetchMock = vi.fn(async (url: string) => {
      if (url === '/api/example-study') return { ok: false }
      return {
        ok: true,
        json: async () => ({ studies: [], more_results: false, next_page_token: null }),
      }
    })
    vi.stubGlobal('fetch', fetchMock)
    const wrapper = mount(App)
    await flushPromises()
    await wrapper.get('input[name="condition"]').setValue('καρκίνος μαστού')
    expect(wrapper.get('button[type="submit"]').attributes('disabled')).toBeDefined()
    expect(wrapper.get('.term-suggestion').text()).toContain('breast cancer')
    expect(wrapper.get('.term-suggestion a').attributes('href')).toMatch(/^https:\/\//)
    await wrapper.get('form').trigger('submit')
    expect(fetchMock).not.toHaveBeenCalledWith('/api/studies/search', expect.anything())
    await wrapper.get('button[name="use-suggested-term"]').trigger('click')
    expect((wrapper.get('input[name="condition"]').element as HTMLInputElement).value).toBe(
      'breast cancer',
    )
    expect(wrapper.get('.chosen-term').text()).toContain('καρκίνος μαστού')
    expect(wrapper.get('.chosen-term a').attributes('href')).toMatch(/^https:\/\//)
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/studies/search',
      expect.objectContaining({
        body: JSON.stringify({ condition: 'breast cancer', open_studies_only: false }),
      }),
    )
    await wrapper.get('input[name="condition"]').setValue('diabetes')
    expect(wrapper.find('.chosen-term').exists()).toBe(false)
  })

  it('does not suggest or submit an unsupported Greek sentence', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: false })
    vi.stubGlobal('fetch', fetchMock)
    const wrapper = mount(App)
    await flushPromises()
    await wrapper.get('input[name="condition"]').setValue('Δεν έχω διαβήτη τύπου 2')
    expect(wrapper.find('.term-suggestion').exists()).toBe(false)
    expect(wrapper.get('button[type="submit"]').attributes('disabled')).toBeDefined()
    await wrapper.get('form').trigger('submit')
    expect(fetchMock).not.toHaveBeenCalledWith('/api/studies/search', expect.anything())
  })
})
