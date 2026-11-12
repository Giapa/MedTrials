export function classifySuggestion(
  expected: string | null,
  actual: string | null,
): 'matched' | 'missed' | 'wrong' | 'unsafe' {
  if (expected === actual) return 'matched'
  if (expected === null) return 'unsafe'
  if (actual === null) return 'missed'
  return 'wrong'
}
