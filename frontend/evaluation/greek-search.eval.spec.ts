import { mount, flushPromises } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import StudySearch from '../src/StudySearch.vue'
import { interfaceCopy } from '../src/interface-copy'
import cases from './greek-search-cases.json'
import { classifySuggestion } from './greek-score'

afterEach(() => vi.unstubAllGlobals())

describe('Greek search examples', () => {
  it.each([
    { name: 'Development', examples: cases.cases },
    { name: 'Follow-up', examples: cases.followup_cases },
  ])('measures $name examples through the search form', async ({ name, examples }) => {
    expect(new Set(examples.map((example) => example.id)).size).toBe(examples.length)
    expect(examples.some((example) => example.expected === null)).toBe(true)
    expect(examples.some((example) => example.expected !== null)).toBe(true)
    for (const example of examples) {
      if (example.expected !== null) expect(Object.keys(cases.sources)).toContain(example.source)
    }
    const outcomes: { id: string; result: ReturnType<typeof classifySuggestion> }[] = []
    const bypasses: string[] = []
    const missingSources: string[] = []
    const wrongRequests: string[] = []
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ studies: [], more_results: false, next_page_token: null }),
    })
    vi.stubGlobal('fetch', fetchMock)

    for (const example of examples) {
      fetchMock.mockClear()
      const wrapper = mount(StudySearch, { props: { copy: interfaceCopy.el, language: 'el' } })
      await wrapper.get('input[name="condition"]').setValue(example.query)
      const suggestion = wrapper.find('.term-suggestion strong')
      const actual = suggestion.exists() ? suggestion.text() : null
      outcomes.push({ id: example.id, result: classifySuggestion(example.expected, actual) })

      await wrapper.get('form').trigger('submit')
      if (
        fetchMock.mock.calls.length ||
        wrapper.get('button[type="submit"]').attributes('disabled') === undefined
      ) {
        bypasses.push(example.id)
      }

      if (actual !== null) {
        if (!wrapper.find('.term-suggestion a[href^="https://"]').exists())
          missingSources.push(example.id)
        await wrapper.get('button[name="use-suggested-term"]').trigger('click')
        if (fetchMock.mock.calls.length) bypasses.push(example.id)
        await wrapper.get('form').trigger('submit')
        await flushPromises()
        const request = fetchMock.mock.calls[0]?.[1]
        if (!request || JSON.parse(String(request.body)).condition !== actual)
          wrongRequests.push(example.id)
      }
      wrapper.unmount()
    }

    const positive = examples.filter((example) => example.expected !== null)
    const abstain = examples.filter((example) => example.expected === null)
    const ids = (result: 'matched' | 'missed' | 'wrong' | 'unsafe') =>
      outcomes.filter((outcome) => outcome.result === result).map((outcome) => outcome.id)
    const matched = new Set(ids('matched'))
    console.log(
      `${name}: ${positive.filter((example) => matched.has(example.id)).length}/${positive.length} expected suggestions matched.`,
    )
    console.log(
      `Abstention examples: ${abstain.filter((example) => matched.has(example.id)).length}/${abstain.length} produced no suggestion.`,
    )
    console.log(`Missed: ${ids('missed').join(', ') || 'none'}`)
    console.log(`Wrong term: ${ids('wrong').join(', ') || 'none'}`)
    console.log(
      `Unexpected suggestion where abstention was expected: ${ids('unsafe').join(', ') || 'none'}`,
    )

    expect(ids('wrong')).toEqual([])
    expect(ids('unsafe')).toEqual([])
    expect(bypasses).toEqual([])
    expect(missingSources).toEqual([])
    expect(wrongRequests).toEqual([])
  })
})
