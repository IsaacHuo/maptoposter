import { afterEach, describe, expect, it, vi } from 'vitest'
import type { PosterRequest } from './types'
import { prepareMap, searchPlaces } from './api'

function jsonResponse(payload: unknown): Response {
  return { ok: true, json: async () => payload } as unknown as Response
}

describe('API network errors', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('replaces the browser Failed to fetch message with actionable guidance', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))

    await expect(prepareMap({} as PosterRequest)).rejects.toThrow(
      'The map request was interrupted. Please retry or zoom in to a smaller area.',
    )
  })
})

describe('place search language', () => {
  afterEach(() => vi.unstubAllGlobals())

  it.each(['zh', 'zh-CN', 'zh-Hans'])('requests lang=cn for the %s locale', async (language) => {
    vi.stubGlobal('navigator', { language })
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse([]))
    vi.stubGlobal('fetch', fetchMock)

    await searchPlaces('Tokyo')

    const url = String(fetchMock.mock.calls[0][0])
    expect(url).toContain('lang=cn')
    expect(url).not.toContain('lang=zh')
  })

  it('requests lang=en for non-Chinese locales', async () => {
    vi.stubGlobal('navigator', { language: 'en-US' })
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse([]))
    vi.stubGlobal('fetch', fetchMock)

    await searchPlaces('Tokyo')

    expect(String(fetchMock.mock.calls[0][0])).toContain('lang=en')
  })
})
