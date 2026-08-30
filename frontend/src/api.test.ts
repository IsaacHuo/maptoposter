import { afterEach, describe, expect, it, vi } from 'vitest'
import type { PosterRequest } from './types'
import { prepareMap } from './api'

describe('API network errors', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('replaces the browser Failed to fetch message with actionable guidance', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))

    await expect(prepareMap({} as PosterRequest)).rejects.toThrow(
      'The map request was interrupted. Please retry or zoom in to a smaller area.',
    )
  })
})
