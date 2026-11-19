import type { ApiEnvelope } from './types'

/** Uniform fetch client for the T-05 envelope.
 * It never echoes a connection string, never logs a URL, and never fabricates
 * fallback rows when the backend has not implemented an endpoint yet.
 */
export class ApiClientError extends Error {
  readonly code: string
  readonly status: number
  readonly requestId: string
  readonly data: unknown

  constructor(
    message: string,
    options: { code: string; status: number; requestId?: string; data?: unknown },
  ) {
    super(message)
    this.name = 'ApiClientError'
    this.code = options.code
    this.status = options.status
    this.requestId = options.requestId ?? '-'
    this.data = options.data ?? null
  }
}

export const DEFAULT_API_BASE_URL = '/api/v1'

export interface ApiClientOptions {
  baseUrl?: string
  fetchImpl?: typeof fetch
}

export class ApiClient {
  private readonly baseUrl: string
  private readonly fetchImpl?: typeof fetch

  constructor(options: ApiClientOptions = {}) {
    const configured = options.baseUrl ?? import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE_URL
    this.baseUrl = configured.replace(/\/$/, '')
    this.fetchImpl = options.fetchImpl
  }

  get baseURL(): string {
    return this.baseUrl
  }

  async request<T>(path: string, init: RequestInit = {}): Promise<ApiEnvelope<T>> {
    const suffix = path.startsWith('/') ? path : `/${path}`
    const headers = new Headers(init.headers)
    headers.set('Accept', 'application/json')

    const doFetch = this.fetchImpl ?? globalThis.fetch
    let response: Response
    try {
      response = await doFetch(`${this.baseUrl}${suffix}`, { ...init, headers })
    } catch {
      throw new ApiClientError('无法连接 API', { code: 'NETWORK_ERROR', status: 0 })
    }

    let payload: ApiEnvelope<T>
    try {
      payload = (await response.json()) as ApiEnvelope<T>
    } catch {
      throw new ApiClientError('API 响应不是合法 JSON', {
        code: 'INVALID_RESPONSE',
        status: response.status,
      })
    }

    if (!payload || typeof payload.code !== 'string') {
      throw new ApiClientError('API 响应缺少统一 envelope', {
        code: 'INVALID_RESPONSE',
        status: response.status,
      })
    }

    if (payload.code !== 'OK') {
      throw new ApiClientError(payload.message, {
        code: payload.code,
        status: response.status,
        requestId: payload.request_id,
        data: payload.data,
      })
    }
    return payload
  }

  get<T>(path: string, init: RequestInit = {}): Promise<ApiEnvelope<T>> {
    return this.request<T>(path, { ...init, method: 'GET' })
  }
}

export function isNotImplemented(error: unknown): boolean {
  return error instanceof ApiClientError && error.code === 'NOT_IMPLEMENTED'
}

export const apiClient = new ApiClient()
