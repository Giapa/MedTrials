export function isSmallCellSearch(term: string): boolean {
  const normalized = term
    .trim()
    .toLowerCase()
    .replace(/[\s\-\u2010-\u2015]+/g, ' ')
  return normalized === 'small cell lung cancer'
}

export function mentionsNonSmallCell(title: string, condition: string | null): boolean {
  const pattern = /\bnon[\s\-\u2010-\u2015]+small[\s\-\u2010-\u2015]+cell\b/i
  return pattern.test(title) || (condition !== null && pattern.test(condition))
}
