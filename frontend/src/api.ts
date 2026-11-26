import type { Lang, Profile, Result } from './types'

export class PlanError extends Error {
  readonly code: 'invalid' | 'rate_limited' | 'network' | 'server'
  readonly field: string | null

  constructor(code: PlanError['code'], field: string | null = null) {
    super(code)
    this.code = code
    this.field = field
  }
}

export async function createPlan(profile: Profile, lang: Lang): Promise<Result> {
  let response: Response
  try {
    response = await fetch('/api/plan', {
      method: 'POST',
      // The server refuses requests without this header (protection against other websites).
      headers: { 'content-type': 'application/json', 'X-Requested-With': 'dimafit' },
      body: JSON.stringify({ profile, lang }),
    })
  } catch {
    throw new PlanError('network')
  }
  if (response.ok) return response.json()
  let body: { error?: string; field?: string } = {}
  try {
    body = await response.json()
  } catch {
    // not JSON
  }
  if (response.status === 422) throw new PlanError('invalid', body.field ?? null)
  if (response.status === 429) throw new PlanError('rate_limited')
  throw new PlanError('server')
}
