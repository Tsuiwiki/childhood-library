import { describe, expect, it, vi } from 'vitest'
import { ApiClient, ApiClientError, isNotImplemented } from '../src/api/client'
import { listDomain } from '../src/api/endpoints'
import type { ApiEnvelope } from '../src/api/types'

function envelope<T>(data: T, code = 'OK'): ApiEnvelope<T> {
  return { code, message: code === 'OK' ? 'success' : 'failed', data, request_id: 'rid-1' }
}

function fakeResponse(body: unknown, status = 200): Response {
  return { status, json: async () => body } as Response
}

describe('ApiClient', () => {
  it('returns the backend envelope unchanged on OK', async () => {
    const fetchImpl = vi.fn(async () => fakeResponse(envelope({ status: 'ok' })))
    const client = new ApiClient({ baseUrl: '/api/v1/', fetchImpl: fetchImpl as unknown as typeof fetch })

    const result = await client.get<{ status: string }>('/healthz')

    expect(client.baseURL).toBe('/api/v1')
    expect(result.code).toBe('OK')
    expect(result.request_id).toBe('rid-1')
    expect(result.data).toEqual({ status: 'ok' })
    expect(fetchImpl).toHaveBeenCalledOnce()
  })

  it('joins the path and sets Accept without echoing any host', async () => {
    const fetchImpl = vi.fn(async () => fakeResponse(envelope(null)))
    const client = new ApiClient({ baseUrl: '/api/v1', fetchImpl: fetchImpl as unknown as typeof fetch })

    await client.get('media/capabilities')

    const [url, init] = fetchImpl.mock.calls[0] as unknown as [string, RequestInit]
    expect(url).toBe('/api/v1/media/capabilities')
    expect((init.headers as Headers).get('Accept')).toBe('application/json')
    expect(init.method).toBe('GET')
  })

  it('maps a 501 response to NOT_IMPLEMENTED with details', async () => {
    const body = envelope({ domain: 'catalog', planned_from: 'post-T-06' }, 'NOT_IMPLEMENTED')
    const fetchImpl = vi.fn(async () => fakeResponse(body, 501))
    const client = new ApiClient({ baseUrl: '/api/v1', fetchImpl: fetchImpl as unknown as typeof fetch })

    await expect(client.get('/catalog')).rejects.toMatchObject({
      name: 'ApiClientError',
      code: 'NOT_IMPLEMENTED',
      status: 501,
      requestId: 'rid-1',
      data: { domain: 'catalog', planned_from: 'post-T-06' },
    })

    try {
      await client.get('/catalog')
    } catch (error) {
      expect(isNotImplemented(error)).toBe(true)
      expect(error).toBeInstanceOf(ApiClientError)
    }
  })

  it('rejects non-JSON and envelope-less responses', async () => {
    const broken = vi.fn(async () => ({ status: 502, json: async () => { throw new Error('not json') } }))
    const shapeless = vi.fn(async () => fakeResponse({ foo: 'bar' }))
    const client1 = new ApiClient({ fetchImpl: broken as unknown as typeof fetch })
    const client2 = new ApiClient({ fetchImpl: shapeless as unknown as typeof fetch })

    await expect(client1.get('/healthz')).rejects.toMatchObject({ code: 'INVALID_RESPONSE', status: 502 })
    await expect(client2.get('/healthz')).rejects.toMatchObject({ code: 'INVALID_RESPONSE' })
  })

  it('turns a network failure into NETWORK_ERROR', async () => {
    const fetchImpl = vi.fn(async () => { throw new Error('offline') })
    const client = new ApiClient({ fetchImpl: fetchImpl as unknown as typeof fetch })
    await expect(client.get('/healthz')).rejects.toMatchObject({ code: 'NETWORK_ERROR', status: 0 })
  })

  it('uses a relative default baseURL', () => {
    const client = new ApiClient({ fetchImpl: (async () => fakeResponse(envelope(null))) as unknown as typeof fetch })
    expect(client.baseURL).toBe('/api/v1')
    expect(client.baseURL.startsWith('http')).toBe(false)
  })
})

describe('listDomain', () => {
  it('validates limit before issuing a request', () => {
    expect(() => listDomain('catalog', 0)).toThrow(RangeError)
    expect(() => listDomain('catalog', 101)).toThrow(RangeError)
    expect(() => listDomain('catalog', 1.5)).toThrow(RangeError)
  })
})
