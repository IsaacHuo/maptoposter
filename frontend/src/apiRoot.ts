export const DEFAULT_API_ROOT = '/api/v1'

/**
 * Resolve the API base URL from `VITE_API_URL`.
 *
 * The browser build keeps the relative default so the Vite proxy keeps working.
 * A Capacitor build must supply an absolute URL, because the packaged WebView
 * serves the app from https://localhost.
 */
export function resolveApiRoot(configured?: string): string {
  const trimmed = configured?.trim()
  if (!trimmed) return DEFAULT_API_ROOT
  return trimmed.replace(/\/+$/, '')
}

/** Detect a Capacitor native WebView without importing @capacitor/core into web tests. */
export function isNativeShell(): boolean {
  const capacitor = (globalThis as { Capacitor?: { isNativePlatform?: () => boolean } }).Capacitor
  try {
    return capacitor?.isNativePlatform?.() === true
  } catch {
    return false
  }
}

/** Return an actionable message when a native build is missing its API origin. */
export function apiRootConfigError(apiRoot: string, native: boolean): string | null {
  if (!native || !apiRoot.startsWith('/')) return null
  return 'This build has no API server configured. Set VITE_API_URL (e.g. http://10.0.2.2:7860/api/v1) and rebuild.'
}
