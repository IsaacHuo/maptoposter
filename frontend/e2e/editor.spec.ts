import { test, expect } from '@playwright/test'

test('editor has a real canvas and responsive controls', async ({ page }) => {
  const styles = [
    ['japanese_ink', 'Japanese Ink', '#f6f4ef', '#111111'],
    ['noir', 'Noir', '#0d0d0f', '#f4f1ea'],
    ['ocean', 'Ocean', '#edf7fb', '#1a3547'],
    ['forest', 'Forest', '#edf3eb', '#263b2b'],
    ['terracotta', 'Terracotta', '#f7eee7', '#4b2d23'],
  ].map(([id, name, background, text]) => ({
    id, name, description: '', preview: `/style-previews/${id}.webp`, background, text,
    water: '#d8d5cf', parks: '#e6e3dd', road_motorway: '#111111', road_primary: '#222222',
    road_secondary: '#333333', road_tertiary: '#444444', road_residential: '#555555', road_default: '#444444', gradient: '#ffffff',
  }))
  await page.route('**/api/v1/styles', async (route) => route.fulfill({ json: styles }))
  await page.route('**/api/v1/map-data/prepare', async (route) => route.fulfill({ json: { map_data_id: 'a'.repeat(64), cache_hit: true } }))
  await page.route('**/api/v1/posters/preview', async (route) => route.fulfill({ status: 200, path: 'public/sample-poster.webp' }))
  await page.goto('/')
  await expect(page.getByText('MapToPoster')).toBeVisible()
  await expect(page.getByAltText(/Poster preview/)).toBeVisible()
  await page.getByRole('main').getByRole('button', { name: 'Zoom in' }).click()
  await expect(page.getByText('92%')).toBeVisible()
  await expect(page.locator('.preview-status')).toContainText('Preview updated', { timeout: 5000 })
  await page.getByRole('button', { name: /Export options/ }).click()
  await expect(page.getByText('SVG · Vector')).toBeVisible()
  await page.screenshot({ path: 'test-results/editor-desktop.png', fullPage: true })
  await page.getByRole('button', { name: /Export options/ }).click()
  await page.setViewportSize({ width: 390, height: 844 })
  await page.screenshot({ path: 'test-results/editor-mobile.png', fullPage: true })
})
