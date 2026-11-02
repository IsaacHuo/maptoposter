import { afterEach, describe, expect, it } from 'vitest'
import { apiRootConfigError, DEFAULT_API_ROOT, isNativeShell, resolveApiRoot } from './apiRoot'

describe('resolveApiRoot', () => {
  it('keeps the relative default for the browser build', () => {
    expect(resolveApiRoot(undefined)).toBe(DEFAULT_API_ROOT)
    expect(resolveApiRoot('   ')).toBe(DEFAULT_API_ROOT)
  })

  it('uses the configured absolute URL without a trailing slash', () => {
    expect(resolveApiRoot(' http://10.0.2.2:7860/api/v1/ ')).toBe('http://10.0.2.2:7860/api/v1')
  })
})

describe('apiRootConfigError', () => {
  it('flags a relative API root inside the native shell', () => {
    expect(apiRootConfigError(DEFAULT_API_ROOT, true)).toContain('VITE_API_URL')
  })

  it('accepts an absolute API root and the plain web build', () => {
    expect(apiRootConfigError('http://10.0.2.2:7860/api/v1', true)).toBeNull()
    expect(apiRootConfigError(DEFAULT_API_ROOT, false)).toBeNull()
  })
})

describe('isNativeShell', () => {
  afterEach(() => {
    delete (globalThis as { Capacitor?: unknown }).Capacitor
  })

  it('is false in a plain browser', () => {
    expect(isNativeShell()).toBe(false)
  })

  it('follows the Capacitor runtime flag', () => {
    ;(globalThis as { Capacitor?: unknown }).Capacitor = { isNativePlatform: () => true }
    expect(isNativeShell()).toBe(true)
  })
})
