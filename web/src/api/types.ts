/** Contracts mirror the backend, never invent a second source of truth.
 * envelope: app/schemas/common.py L7-L12
 * codes:    app/core/errors.py L17-L26
 * domains:  app/api/v1/router.py DOMAIN_NAMES
 */

export const ERROR_CODES = [
  'OK',
  'VALIDATION_ERROR',
  'NOT_FOUND',
  'METHOD_NOT_ALLOWED',
  'NOT_IMPLEMENTED',
  'HTTP_ERROR',
  'FORBIDDEN',
  'NOT_READY',
  'INTERNAL_ERROR',
] as const

export type ErrorCode = (typeof ERROR_CODES)[number]

export const DOMAIN_NAMES = [
  'catalog',
  'versions',
  'sources',
  'rights',
  'reviews',
  'media',
  'ingestion',
] as const

export type DomainName = (typeof DOMAIN_NAMES)[number]

export interface ApiEnvelope<T = unknown> {
  code: string
  message: string
  data: T | null
  request_id: string
}

export interface HealthData {
  status: string
  service: string
  environment: string
  version: string
  python_version: string
  api_prefix: string
  domains: string[]
  checks: { database_tcp: string; database_sql: string }
}

export interface ReadyzData {
  ready: boolean
  checks: { database_sql: string }
}

export interface MediaCapabilitiesData {
  stage: string
  provider: string
  root_exists: boolean
  read_only: boolean
  flat_object_count: number
  operations: string[]
  rights_gate: string[]
  public_url_issued: boolean
  note: string
}

/** details payload of the seven placeholder endpoints (app/api/v1/_skeleton.py L19-L23) */
export interface NotImplementedDetails {
  domain: string
  planned_from: string
}
