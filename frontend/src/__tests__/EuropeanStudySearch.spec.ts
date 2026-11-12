import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, expect, it, vi } from 'vitest'
import EuropeanStudySearch from '../EuropeanStudySearch.vue'
import { interfaceCopy } from '../interface-copy'

afterEach(() => vi.unstubAllGlobals())

it('searches the European registry and lets the user choose a result', async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      studies: [
        {
          id: '2025-522873-12-00',
          title: 'Breast cancer study',
          condition: 'Advanced breast cancer',
          source_url: 'https://euclinicaltrials.eu/ctis-public/view/2025-522873-12-00',
        },
      ],
      page: 1,
      total: 1,
      more_results: false,
    }),
  })
  vi.stubGlobal('fetch', fetchMock)
  const wrapper = mount(EuropeanStudySearch, { props: { copy: interfaceCopy.el } })
  await wrapper.get('input[name="eu-condition"]').setValue('breast cancer')
  await wrapper.get('form').trigger('submit')
  await flushPromises()
  expect(fetchMock).toHaveBeenCalledWith(
    '/api/eu-studies/search',
    expect.objectContaining({ body: JSON.stringify({ condition: 'breast cancer', page: 1 }) }),
  )
  expect(wrapper.text()).toContain('Breast cancer study')
  expect(wrapper.get('.eu-search-results a').attributes('href')).toBe(
    'https://euclinicaltrials.eu/ctis-public/view/2025-522873-12-00',
  )
  await wrapper.get('button[name="eu-select"]').trigger('click')
  expect(wrapper.emitted('select')?.[0]).toEqual(['2025-522873-12-00'])
})

it('requires a Greek suggestion to be selected before sending a search', async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({ studies: [], total: 0, page: 1, more_results: false }),
  })
  vi.stubGlobal('fetch', fetchMock)
  const wrapper = mount(EuropeanStudySearch, { props: { copy: interfaceCopy.el } })
  await wrapper.get('input[name="eu-condition"]').setValue('Έχω διαβήτη τύπου 2')
  expect(wrapper.get('button[type="submit"]').attributes('disabled')).toBeDefined()
  await wrapper.get('form').trigger('submit')
  expect(fetchMock).not.toHaveBeenCalled()
  await wrapper.get('button[name="eu-use-term"]').trigger('click')
  await wrapper.get('form').trigger('submit')
  await flushPromises()
  expect(fetchMock).toHaveBeenCalledWith(
    '/api/eu-studies/search',
    expect.objectContaining({ body: JSON.stringify({ condition: 'type 2 diabetes', page: 1 }) }),
  )
})

it('preserves results after a busy page and retries the submitted search', async () => {
  const firstStudy = {
    id: '2025-522873-12-00',
    title: 'First study',
    condition: null,
    source_url: 'https://euclinicaltrials.eu/ctis-public/view/2025-522873-12-00',
  }
  const secondStudy = {
    id: '2024-518933-28-01',
    title: 'Second study',
    condition: null,
    source_url: 'https://euclinicaltrials.eu/ctis-public/view/2024-518933-28-01',
  }
  let attempts = 0
  const fetchMock = vi.fn(async (_url: string, options: RequestInit) => {
    const body = JSON.parse(String(options.body))
    if (body.page === 1)
      return {
        ok: true,
        json: async () => ({ studies: [firstStudy], total: 2, page: 1, more_results: true }),
      }
    attempts += 1
    if (attempts === 1) return { ok: false, status: 429 }
    return {
      ok: true,
      json: async () => ({
        studies: [firstStudy, secondStudy],
        total: 2,
        page: 2,
        more_results: false,
      }),
    }
  })
  vi.stubGlobal('fetch', fetchMock)
  const wrapper = mount(EuropeanStudySearch, { props: { copy: interfaceCopy.el } })
  await wrapper.get('input[name="eu-condition"]').setValue('breast cancer')
  await wrapper.get('form').trigger('submit')
  await flushPromises()
  await wrapper.get('input[name="eu-condition"]').setValue('asthma')
  await wrapper.get('button[name="eu-load-more"]').trigger('click')
  await flushPromises()
  expect(wrapper.text()).toContain('First study')
  expect(wrapper.text()).toContain('Τα προηγούμενα αποτελέσματα παραμένουν διαθέσιμα')
  await wrapper.get('button[name="eu-load-more"]').trigger('click')
  await flushPromises()
  expect(fetchMock).toHaveBeenLastCalledWith(
    '/api/eu-studies/search',
    expect.objectContaining({ body: JSON.stringify({ condition: 'breast cancer', page: 2 }) }),
  )
  expect(wrapper.findAll('.eu-search-results article')).toHaveLength(2)
  expect(wrapper.text()).toContain('Second study')
})
