import { describe, expect, it } from 'vitest'
import { findGreekConditionTerm, hasGreekText } from '../greek-condition-terms'

describe('Greek condition suggestions', () => {
  it.each([
    ['  ΚΑΡΚΙΝΟΣ   ΜΑΣΤΟΥ  ', 'breast cancer'],
    ['διαβήτης τύπου 2', 'type 2 diabetes'],
    ['μικροκυτταρικός καρκίνος πνεύμονα', 'small cell lung cancer'],
    ['μη μικροκυτταρικός καρκίνος πνεύμονα', 'non-small cell lung cancer'],
    ['σκληρόδερμα', 'scleroderma'],
  ])('suggests a sourced English term for %s', (input, english) => {
    const suggestion = findGreekConditionTerm(input)
    expect(suggestion?.english).toBe(english)
    expect(suggestion?.sourceUrl).toMatch(/^https:\/\//)
  })

  it.each([
    'Δεν έχω διαβήτη τύπου 2',
    'Έχω διαβήτη τύπου 2',
    'καρκίνος μαστού με μεταστάσεις',
    'άγνωστη πάθηση',
  ])('does not guess the meaning of %s', (input) => {
    expect(findGreekConditionTerm(input)).toBeNull()
    expect(hasGreekText(input)).toBe(true)
  })

  it('does not flag an English condition as Greek', () => {
    expect(hasGreekText('breast cancer')).toBe(false)
  })
})
