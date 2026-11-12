import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, expect, it, vi } from 'vitest'
import EuropeanStudyLookup from '../EuropeanStudyLookup.vue'
import { interfaceCopy } from '../interface-copy'

afterEach(() => vi.unstubAllGlobals())

it('shows Greek criteria, labels English fallback, and links to the source', async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      id: '2025-522873-12-00',
      title: { english: 'Public title', greek: 'Δημόσιος τίτλος' },
      inclusion: [{ english: 'Adult participants', greek: 'Ενήλικες συμμετέχοντες' }],
      exclusion: [{ english: 'Prior treatment', greek: null }],
      source_url: 'https://euclinicaltrials.eu/ctis-public/view/2025-522873-12-00',
    }),
  })
  vi.stubGlobal('fetch', fetchMock)
  const wrapper = mount(EuropeanStudyLookup, { props: { copy: interfaceCopy.el, language: 'el' } })
  await wrapper.get('input[name="eu-trial-id"]').setValue('2025-522873-12-00')
  await wrapper.get('.eu-lookup-form').trigger('submit')
  await flushPromises()
  expect(fetchMock).toHaveBeenCalledWith('/api/eu-studies/2025-522873-12-00')
  expect(wrapper.text()).toContain('Δημόσιος τίτλος')
  expect(wrapper.text()).toContain('Ενήλικες συμμετέχοντες')
  expect(wrapper.text()).toContain('Prior treatment')
  expect(wrapper.text()).toContain('Δεν παρέχεται ελληνική μετάφραση')
  expect(wrapper.get('.eu-result a').attributes('href')).toBe(
    'https://euclinicaltrials.eu/ctis-public/view/2025-522873-12-00',
  )
})

it('reports no matching Greek record and avoids inventing details', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 404 }))
  const wrapper = mount(EuropeanStudyLookup, { props: { copy: interfaceCopy.el, language: 'el' } })
  await wrapper.get('input[name="eu-trial-id"]').setValue('2025-522873-12-00')
  await wrapper.get('.eu-lookup-form').trigger('submit')
  await flushPromises()
  expect(wrapper.get('[role="alert"]').text()).toContain('Δεν βρέθηκε')
  expect(wrapper.find('.eu-result').exists()).toBe(false)
})

it('rejects an invalid number without contacting the registry', async () => {
  const fetchMock = vi.fn()
  vi.stubGlobal('fetch', fetchMock)
  const wrapper = mount(EuropeanStudyLookup, { props: { copy: interfaceCopy.el, language: 'el' } })
  await wrapper.get('input[name="eu-trial-id"]').setValue('not-a-trial-number')
  await wrapper.get('.eu-lookup-form').trigger('submit')
  expect(wrapper.get('[role="alert"]').text()).toContain('2025-522873-12-00')
  expect(fetchMock).not.toHaveBeenCalled()
})

it('rejects a record whose source points to a different trial', async () => {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        id: '2025-522873-12-00',
        title: { english: 'Title', greek: null },
        inclusion: [],
        exclusion: [],
        source_url: 'https://euclinicaltrials.eu/ctis-public/view/2024-111111-11-11',
      }),
    }),
  )
  const wrapper = mount(EuropeanStudyLookup, { props: { copy: interfaceCopy.el, language: 'el' } })
  await wrapper.get('input[name="eu-trial-id"]').setValue('2025-522873-12-00')
  await wrapper.get('.eu-lookup-form').trigger('submit')
  await flushPromises()
  expect(wrapper.get('[role="alert"]').text()).toContain('Δεν ήταν δυνατή')
  expect(wrapper.find('.eu-result').exists()).toBe(false)
})

it('opens a selected search result in the criteria view', async () => {
  const fetchMock = vi.fn(async (url: string) => {
    if (url === '/api/eu-studies/search')
      return {
        ok: true,
        json: async () => ({
          studies: [
            {
              id: '2025-522873-12-00',
              title: 'Study title',
              condition: null,
              source_url: 'https://euclinicaltrials.eu/ctis-public/view/2025-522873-12-00',
            },
          ],
          page: 1,
          total: 1,
          more_results: false,
        }),
      }
    return {
      ok: true,
      json: async () => ({
        id: '2025-522873-12-00',
        title: { english: 'Study title', greek: null },
        inclusion: [],
        exclusion: [],
        source_url: 'https://euclinicaltrials.eu/ctis-public/view/2025-522873-12-00',
      }),
    }
  })
  vi.stubGlobal('fetch', fetchMock)
  const wrapper = mount(EuropeanStudyLookup, {
    props: { copy: interfaceCopy.el, language: 'el' },
    attachTo: document.body,
  })
  await wrapper.get('input[name="eu-condition"]').setValue('breast cancer')
  await wrapper.get('.eu-search form').trigger('submit')
  await flushPromises()
  await wrapper.get('button[name="eu-select"]').trigger('click')
  await flushPromises()
  expect(fetchMock).toHaveBeenCalledWith('/api/eu-studies/2025-522873-12-00')
  expect(wrapper.get('.eu-result').text()).toContain('Study title')
  expect(document.activeElement).toBe(wrapper.get('.eu-lookup-heading').element)
  expect((wrapper.get('input[name="eu-trial-id"]').element as HTMLInputElement).value).toBe(
    '2025-522873-12-00',
  )
})
