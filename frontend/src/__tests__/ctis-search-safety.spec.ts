import { describe, expect, it } from 'vitest'
import { isSmallCellSearch, mentionsNonSmallCell } from '../ctis-search-safety'

describe('CTIS small-cell search caution', () => {
  it('only recognizes the specific small-cell search term', () => {
    expect(isSmallCellSearch(' SMALL-cell lung cancer ')).toBe(true)
    expect(isSmallCellSearch('non-small cell lung cancer')).toBe(false)
    expect(isSmallCellSearch('small cell lung cancer and asthma')).toBe(false)
  })

  it('finds explicit non-small-cell words in the displayed title or condition', () => {
    expect(mentionsNonSmallCell('Non-small-cell lung cancer', null)).toBe(true)
    expect(mentionsNonSmallCell('Study title', 'Advanced non–small cell lung cancer')).toBe(true)
    expect(mentionsNonSmallCell('Study of small cell cancer', null)).toBe(false)
    expect(mentionsNonSmallCell('Study of NSCLC', null)).toBe(false)
  })
})
