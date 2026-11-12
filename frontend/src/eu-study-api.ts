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

export type EuropeanStudy = z.infer<typeof euStudySchema>
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
