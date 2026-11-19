import { apiClient } from './client'
import type {
  ApiEnvelope,
  DomainName,
  HealthData,
  MediaCapabilitiesData,
  NotImplementedDetails,
  ReadyzData,
} from './types'

export function getHealth(): Promise<ApiEnvelope<HealthData>> {
  return apiClient.get<HealthData>('/healthz')
}

export function getReadyz(): Promise<ApiEnvelope<ReadyzData>> {
  return apiClient.get<ReadyzData>('/readyz')
}

/** T-07 read-only capability state; the response never contains an access URL. */
export function getMediaCapabilities(): Promise<ApiEnvelope<MediaCapabilitiesData>> {
  return apiClient.get<MediaCapabilitiesData>('/media/capabilities')
}

/** The seven domain list endpoints still return 501 (app/api/v1/_skeleton.py).
 * Callers MUST surface NOT_IMPLEMENTED; no local JSON or demo rows as fallback.
 */
export function listDomain(
  domain: DomainName,
  limit = 20,
): Promise<ApiEnvelope<NotImplementedDetails>> {
  if (!Number.isInteger(limit) || limit < 1 || limit > 100) {
    throw new RangeError('limit must be an integer between 1 and 100')
  }
  return apiClient.get<NotImplementedDetails>(`/${domain}?limit=${limit}`)
}
