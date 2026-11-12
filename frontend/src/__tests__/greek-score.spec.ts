import { describe, expect, it } from 'vitest'
import { classifySuggestion } from '../../evaluation/greek-score'

describe('Greek suggestion evaluation', () => {
  it('distinguishes missed, wrong, and unsafe suggestions', () => {
    expect(classifySuggestion('breast cancer', 'breast cancer')).toBe('matched')
    expect(classifySuggestion(null, null)).toBe('matched')
    expect(classifySuggestion('breast cancer', null)).toBe('missed')
    expect(classifySuggestion('breast cancer', 'lung cancer')).toBe('wrong')
    expect(classifySuggestion(null, 'type 2 diabetes')).toBe('unsafe')
  })
})
