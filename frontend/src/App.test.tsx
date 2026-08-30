import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
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

  it('changes zoom and fit state', () => {
    render(<App />)
    expect(screen.getAllByText('82%').length).toBeGreaterThan(0)
    fireEvent.click(screen.getAllByRole('button', { name: 'Zoom in' })[0])
    expect(screen.getAllByText('92%').length).toBeGreaterThan(0)
    fireEvent.click(screen.getAllByRole('button', { name: 'Fit' })[0])
    expect(screen.getAllByText('82%').length).toBeGreaterThan(0)
  })
})
