import { z } from 'zod'

const studySchema = z.object({
  id: z.literal('NCT02798055'),
  title: z.string().min(1),
  summary: z.string().nullable(),
  status: z.string().nullable(),
  last_updated: z.string().nullable(),
  locations: z.array(z.object({ facility: z.string().nullable(), city: z.string().nullable() })),
  source_url: z.literal('https://clinicaltrials.gov/study/NCT02798055'),
})

export type Study = z.infer<typeof studySchema>

export async function fetchExampleStudy(): Promise<Study> {
  const response = await fetch('/api/example-study')
  if (!response.ok) throw new Error('Registry request failed')
  return studySchema.parse(await response.json())
}
