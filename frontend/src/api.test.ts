import { afterEach, describe, expect, it, vi } from 'vitest'
import type { PosterRequest } from './types'
import { exportPoster, prepareMap, searchPlaces } from './api'

function jsonResponse(payload: unknown): Response {
  return { ok: true, json: async () => payload } as unknown as Response
}

function exportResponse(disposition: string): Response {
  return {
    ok: true,
    status: 200,
    headers: { get: (name: string) => (name.toLowerCase() === 'content-disposition' ? disposition : null) },
    blob: async () => new Blob(['poster']),
  } as unknown as Response
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

describe('export download filename', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('prefers the RFC 5987 filename* for Chinese names', async () => {
    const disposition =
      'attachment; filename="japanese-ink-20261017.png"; ' +
      "filename*=UTF-8''%E5%8C%97%E4%BA%AC%E5%B8%82-japanese-ink-20261017.png"
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(exportResponse(disposition)))

    const { filename } = await exportPoster('a'.repeat(64), {} as PosterRequest, 'png', 300)

    expect(filename).toBe('北京市-japanese-ink-20261017.png')
  })

  it('falls back to the ASCII filename when filename* is absent', async () => {
    const disposition = 'attachment; filename="beijing-japanese-ink-20261017.png"'
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(exportResponse(disposition)))

    const { filename } = await exportPoster('a'.repeat(64), {} as PosterRequest, 'png', 300)

    expect(filename).toBe('beijing-japanese-ink-20261017.png')
  })

  it('uses the format-based default when the header is missing', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(exportResponse('')))

    const { filename } = await exportPoster('a'.repeat(64), {} as PosterRequest, 'pdf', 300)

    expect(filename).toBe('maptoposter.pdf')
  })
})
