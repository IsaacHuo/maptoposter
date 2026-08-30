import { render } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { MapViewport } from './MapViewport'

const mapMock = vi.hoisted(() => ({
  addControl: vi.fn(),
  fitBounds: vi.fn(),
  getBounds: vi.fn(() => ({ getWest: () => 113.9, getSouth: () => 22.4, getEast: () => 114.2, getNorth: () => 22.7 })),
  getCenter: vi.fn(() => ({ lng: 114.0545, lat: 22.5446 })),
  getZoom: vi.fn(() => 10.8),
  on: vi.fn(),
  remove: vi.fn(),
}))
const mapConstructor = vi.hoisted(() => vi.fn(function MapMock() { return mapMock }))

vi.mock('maplibre-gl', () => ({
  AttributionControl: vi.fn(),
  Map: mapConstructor,
  NavigationControl: vi.fn(),
}))

describe('MapViewport', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    Object.defineProperty(HTMLElement.prototype, 'clientWidth', { configurable: true, value: 320 })
    Object.defineProperty(HTMLElement.prototype, 'clientHeight', { configurable: true, value: 220 })
    vi.stubGlobal('ResizeObserver', class {
      observe() {}
      disconnect() {}
    })
  })

  it('does not recreate or refit the map when a move event updates only the bbox', () => {
    const onViewportChange = vi.fn()
    const location = { longitude: 114.0545, latitude: 22.5446 }
    const initialBBox = { west: 114.0058, south: 22.4996, east: 114.1032, north: 22.5896 }
    const { rerender } = render(<MapViewport {...location} bbox={initialBBox} onViewportChange={onViewportChange} />)

    expect(mapConstructor).toHaveBeenCalledTimes(1)
    expect(mapMock.fitBounds).toHaveBeenCalledTimes(1)

    rerender(<MapViewport {...location} bbox={{ west: 113.98, south: 22.47, east: 114.13, north: 22.62 }} onViewportChange={onViewportChange} />)

    expect(mapConstructor).toHaveBeenCalledTimes(1)
    expect(mapMock.fitBounds).toHaveBeenCalledTimes(1)
    expect(mapMock.remove).not.toHaveBeenCalled()
  })
})
