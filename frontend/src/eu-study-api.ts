import { z } from 'zod'
import { RegistryBusyError } from './study-api'

const trialIdPattern = /^[0-9]{4}-[0-9]{6}-[0-9]{2}-[0-9]{2}$/
const textSchema = z.object({ english: z.string().min(1), greek: z.string().min(1).nullable() })
const euStudySchema = z
  .object({
    id: z.string().regex(trialIdPattern),
    title: textSchema,
    inclusion: z.array(textSchema),
    exclusion: z.array(textSchema),
    source_url: z.string(),
  })
  .refine(
    (study) => study.source_url === `https://euclinicaltrials.eu/ctis-public/view/${study.id}`,
  )

const euSearchSchema = z.object({
  studies: z.array(
    z
      .object({
        id: z.string().regex(trialIdPattern),
        title: z.string().min(1),
        condition: z.string().nullable(),
        source_url: z.string(),
      })
      .refine(
        (study) => study.source_url === `https://euclinicaltrials.eu/ctis-public/view/${study.id}`,
      ),
  ),
  total: z.number().int().nonnegative(),
  page: z.number().int().positive(),
  more_results: z.boolean(),
})

export type EuropeanStudy = z.infer<typeof euStudySchema>
export type EuropeanSearchResults = z.infer<typeof euSearchSchema>
export class EuropeanStudyNotFoundError extends Error {}
export function isEuropeanTrialNumber(value: string): boolean {
  return trialIdPattern.test(value)
}

export async function fetchEuropeanStudy(id: string): Promise<EuropeanStudy> {
  const response = await fetch(`/api/eu-studies/${encodeURIComponent(id)}`)
  if (response.status === 404) throw new EuropeanStudyNotFoundError()
  if (response.status === 429) throw new RegistryBusyError()
  if (!response.ok) throw new Error('European registry unavailable')
  const study = euStudySchema.parse(await response.json())
  if (study.id !== id) throw new Error('Unexpected trial number')
  return study
}

export async function searchEuropeanStudies(
  condition: string,
  page: number,
): Promise<EuropeanSearchResults> {
  const response = await fetch('/api/eu-studies/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ condition, page }),
  })
  if (response.status === 429) throw new RegistryBusyError()
  if (!response.ok) throw new Error('European registry unavailable')
  const results = euSearchSchema.parse(await response.json())
  if (results.page !== page) throw new Error('Unexpected page')
  return results
}
