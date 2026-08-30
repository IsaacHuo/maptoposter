import type { LocationResult, PosterRequest, StylePreset } from './types'

const API_ROOT = import.meta.env.VITE_API_URL ?? '/api/v1'

async function request(url: string, init: RequestInit | undefined, networkError: string): Promise<Response> {
  try {
    return await fetch(url, init)
  } catch (reason) {
    if (reason instanceof Error && reason.name === 'AbortError') throw reason
    throw new Error(networkError)
  }
}

async function readError(response: Response): Promise<string> {
  try {
    const payload = await response.json() as { detail?: string }
    return payload.detail ?? `Request failed (${response.status})`
  } catch {
    return `Request failed (${response.status})`
  }
}

async function expectJson<T>(response: Response): Promise<T> {
  if (!response.ok) throw new Error(await readError(response))
  return response.json() as Promise<T>
}

export async function getStyles(signal?: AbortSignal): Promise<StylePreset[]> {
  return expectJson(await request(`${API_ROOT}/styles`, { signal }, 'Could not reach the MapToPoster server. Please retry.'))
}

export async function searchPlaces(query: string, signal?: AbortSignal): Promise<LocationResult[]> {
  const params = new URLSearchParams({ q: query, lang: navigator.language.startsWith('zh') ? 'zh' : 'en' })
  return expectJson(await request(`${API_ROOT}/locations/search?${params}`, { signal }, 'Place search was interrupted. Please retry.'))
}

export async function prepareMap(poster: PosterRequest, signal?: AbortSignal): Promise<{ map_data_id: string; cache_hit: boolean }> {
  return expectJson(await request(`${API_ROOT}/map-data/prepare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(poster),
    signal,
  }, 'The map request was interrupted. Please retry or zoom in to a smaller area.'))
}

export async function renderPreview(mapDataId: string, poster: PosterRequest, signal?: AbortSignal): Promise<Blob> {
  const response = await request(`${API_ROOT}/posters/preview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ map_data_id: mapDataId, poster }),
    signal,
  }, 'The preview connection was interrupted. Please retry.')
  if (!response.ok) throw new Error(await readError(response))
  return response.blob()
}

export async function exportPoster(mapDataId: string, poster: PosterRequest, format: 'png' | 'svg' | 'pdf', dpi: number, signal?: AbortSignal): Promise<{ blob: Blob; filename: string }> {
  const response = await request(`${API_ROOT}/posters/export`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ map_data_id: mapDataId, poster, format, dpi }),
    signal,
  }, `The ${format.toUpperCase()} export connection was interrupted. Please retry.`)
  if (!response.ok) throw new Error(await readError(response))
  const disposition = response.headers.get('Content-Disposition') ?? ''
  const filename = disposition.match(/filename="?([^";]+)"?/i)?.[1] ?? `maptoposter.${format}`
  return { blob: await response.blob(), filename }
}
