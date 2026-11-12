import { z } from 'zod'

const studySchema = z
  .object({
    id: z.string().regex(/^NCT[0-9]{8}$/),
    title: z.string().min(1),
    summary: z.string().nullable(),
    eligibility: z.object({
      criteria: z.string().nullable(),
      minimum_age: z.string().nullable(),
      maximum_age: z.string().nullable(),
      sex: z.string().nullable(),
      healthy_volunteers: z.boolean().nullable(),
      gender_based: z.boolean().nullable(),
      gender_description: z.string().nullable(),
    }),
    status: z.string().nullable(),
    last_updated: z.string().nullable(),
    locations: z.array(
      z.object({
        facility: z.string().nullable(),
        city: z.string().nullable(),
        status: z.string().nullable().optional(),
      }),
    ),
    source_url: z.string(),
  })
  .refine((study) => study.source_url === `https://clinicaltrials.gov/study/${study.id}`)

export type Study = z.infer<typeof studySchema>

export class RegistryBusyError extends Error {}

function ensureAvailable(response: Response) {
  if (response.status === 429) throw new RegistryBusyError('Registry connection is busy')
  if (!response.ok) throw new Error('Registry request failed')
}

export async function fetchExampleStudy(): Promise<Study> {
  const response = await fetch('/api/example-study')
  ensureAvailable(response)
  return studySchema.parse(await response.json())
}

const searchResultsSchema = z
  .object({
    studies: z.array(studySchema),
    more_results: z.boolean(),
    next_page_token: z.string().min(1).max(2048).nullable(),
  })
  .refine((response) => response.more_results === (response.next_page_token !== null))
export type SearchResults = z.infer<typeof searchResultsSchema>

export async function searchStudies(
  condition: string,
  openStudiesOnly: boolean,
  pageToken?: string,
) {
  const response = await fetch('/api/studies/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      condition,
      open_studies_only: openStudiesOnly,
      ...(pageToken ? { page_token: pageToken } : {}),
    }),
  })
  ensureAvailable(response)
  return searchResultsSchema.parse(await response.json())
}
