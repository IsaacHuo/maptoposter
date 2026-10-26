/// <reference types="node" />
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import indexHtml from '../index.html?raw'

// Vitest runs with the frontend directory as its root.
const appCss = readFileSync(resolve(process.cwd(), 'src/App.css'), 'utf8')

describe('mobile baseline', () => {
  it('lets the page extend into display cutouts', () => {
    expect(indexHtml).toContain('viewport-fit=cover')
  })

  it('insets the app chrome with safe-area values', () => {
    expect(appCss).toContain('--safe-top: env(safe-area-inset-top')
    expect(appCss).toContain('--safe-bottom: env(safe-area-inset-bottom')
    expect(appCss).toContain('--header: calc(58px + var(--safe-top))')
  })
})
