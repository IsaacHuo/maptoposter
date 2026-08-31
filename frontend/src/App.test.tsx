import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { prepareMap, renderPreview, searchPlaces } from './api'
import App from './App'

vi.mock('./components/MapViewport', () => ({
  MapViewport: () => <div data-testid="map-viewport">map</div>,
}))
vi.mock('./api', () => ({
  getStyles: vi.fn().mockResolvedValue([
    { id: 'japanese_ink', name: 'Japanese Ink', description: '', preview: '', background: '#fff', text: '#111', water: '#ddd', parks: '#eee', road_motorway: '#111', road_primary: '#222', road_secondary: '#333', road_tertiary: '#444', road_residential: '#555', road_default: '#444', gradient: '#fff' },
    { id: 'ocean', name: 'Ocean', description: '', preview: '', background: '#fff', text: '#111', water: '#ace', parks: '#eee', road_motorway: '#111', road_primary: '#222', road_secondary: '#333', road_tertiary: '#444', road_residential: '#555', road_default: '#444', gradient: '#fff' },
  ]),
  prepareMap: vi.fn().mockResolvedValue({ map_data_id: 'a'.repeat(64), cache_hit: true }),
  renderPreview: vi.fn().mockResolvedValue(new Blob(['png'], { type: 'image/png' })),
  searchPlaces: vi.fn().mockResolvedValue([{ display_name: 'Paris, France', latitude: 48.8566, longitude: 2.3522, country: 'France', region: 'Ile-de-France', country_code: 'fr', provider: 'fake' }]),
  exportPoster: vi.fn(),
}))

describe('editor shell', () => {
  beforeEach(() => vi.clearAllMocks())
  afterEach(cleanup)

  it('loads styles and exposes product controls', async () => {
    render(<App />)
    expect(screen.getByText('MapToPoster')).toBeInTheDocument()
    expect(screen.getAllByRole('button', { name: /Export/i })[0]).toBeInTheDocument()
    await waitFor(() => expect(screen.getAllByText('Japanese Ink').length).toBeGreaterThan(0))
    fireEvent.click(screen.getAllByText('Ocean')[0])
    expect(screen.getAllByText('Ocean').length).toBeGreaterThan(0)
  })

  it('supports mobile-style panel switching and search selection', async () => {
    render(<App />)
    await waitFor(() => expect(screen.getAllByText('Japanese Ink').length).toBeGreaterThan(0))
    fireEvent.click(screen.getAllByRole('button', { name: /Location/i })[0])
    const search = screen.getAllByRole('textbox', { name: 'Search a place' })[0]
    fireEvent.change(search, { target: { value: 'Paris' } })
    fireEvent.submit(search.closest('form')!)
    await waitFor(() => expect(screen.getAllByText('Paris, France').length).toBeGreaterThan(0))
    fireEvent.click(screen.getAllByText('Paris, France')[0])
    expect(screen.getAllByText('Paris, France').length).toBeGreaterThan(0)
  })

  it('fills poster text from a selected Chinese location and omits caption', async () => {
    vi.mocked(searchPlaces).mockResolvedValueOnce([{
      display_name: '深圳市, 广东省, 中国', latitude: 22.5431, longitude: 114.0579,
      country: '中国', region: '广东省', country_code: 'cn', provider: 'china-local',
    }])
    render(<App />)
    await waitFor(() => expect(screen.getAllByText('Japanese Ink').length).toBeGreaterThan(0))

    const search = screen.getAllByRole('textbox', { name: 'Search a place' })[0]
    fireEvent.change(search, { target: { value: '深圳' } })
    fireEvent.submit(search.closest('form')!)
    await waitFor(() => expect(screen.getAllByText('深圳市, 广东省, 中国').length).toBeGreaterThan(0))
    fireEvent.click(screen.getAllByText('深圳市, 广东省, 中国')[0])

    expect(screen.getAllByRole('textbox', { name: 'Title' }).map((input) => (input as HTMLInputElement).value)).toEqual(['深圳市'])
    expect(screen.getAllByRole('textbox', { name: 'Subtitle' }).map((input) => (input as HTMLInputElement).value)).toEqual(['广东省'])
    expect(screen.queryByRole('textbox', { name: 'Caption' })).not.toBeInTheDocument()
  })

  it('offers landscape ratios and sends the selected size for generation', async () => {
    render(<App />)
    await waitFor(() => expect(screen.getAllByText('Japanese Ink').length).toBeGreaterThan(0))
    fireEvent.click(screen.getAllByRole('button', { name: 'Size' })[0])
    fireEvent.click(screen.getAllByRole('button', { name: 'Landscape' })[0])
    fireEvent.click(screen.getAllByRole('button', { name: 'landscape 16:9' })[0])

    expect(document.querySelector('.poster-frame')).toHaveStyle({ aspectRatio: String(16 / 9) })
    fireEvent.click(screen.getAllByRole('button', { name: /Generate preview/i })[0])
    await waitFor(() => expect(prepareMap).toHaveBeenCalled())
    expect(prepareMap).toHaveBeenCalledWith(
      expect.objectContaining({ layout: 'classic', size: { preset: '16:9' } }),
      expect.any(AbortSignal),
    )
  })

  it('changes zoom and fit state', () => {
    render(<App />)
    expect(screen.getAllByText('82%').length).toBeGreaterThan(0)
    fireEvent.click(screen.getAllByRole('button', { name: 'Zoom in' })[0])
    expect(screen.getAllByText('92%').length).toBeGreaterThan(0)
    fireEvent.click(screen.getAllByRole('button', { name: 'Fit' })[0])
    expect(screen.getAllByText('82%').length).toBeGreaterThan(0)
  })

  it('waits for an explicit generation request and reports progress', async () => {
    let resolvePrepare!: (value: { map_data_id: string; cache_hit: boolean }) => void
    vi.mocked(prepareMap).mockReturnValueOnce(new Promise((resolve) => { resolvePrepare = resolve }))
    render(<App />)
    await waitFor(() => expect(screen.getAllByText('Japanese Ink').length).toBeGreaterThan(0))

    expect(prepareMap).not.toHaveBeenCalled()
    fireEvent.click(screen.getAllByRole('button', { name: /Generate preview/i })[0])
    expect(prepareMap).toHaveBeenCalledTimes(1)
    expect(screen.getAllByRole('progressbar').length).toBeGreaterThan(0)

    await act(async () => resolvePrepare({ map_data_id: 'a'.repeat(64), cache_hit: false }))
    await waitFor(() => expect(renderPreview).toHaveBeenCalledTimes(1))
    await waitFor(() => expect(screen.getAllByText(/Preview ready in/).length).toBeGreaterThan(0))
  })
})
