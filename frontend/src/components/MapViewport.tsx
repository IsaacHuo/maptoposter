import { useEffect, useRef } from 'react'
import { AttributionControl, Map, NavigationControl, type Map as MapLibreMap } from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import type { BBox } from '../types'

type Props = {
  longitude: number
  latitude: number
  bbox: BBox
  onViewportChange: (bbox: BBox, zoom: number) => void
}

const tileUrl = import.meta.env.VITE_MAP_TILE_URL ?? 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'

export function MapViewport({ longitude, latitude, bbox, onViewportChange }: Props) {
  const container = useRef<HTMLDivElement>(null)
  const mapRef = useRef<MapLibreMap | null>(null)

  useEffect(() => {
    const element = container.current
    if (!element) return
    let map: MapLibreMap | null = null
    const mount = () => {
      if (map || element.clientWidth === 0 || element.clientHeight === 0) return
      map = new Map({
        container: element,
        center: [longitude, latitude],
        zoom: 10.8,
        attributionControl: false,
        style: {
          version: 8,
          sources: { osm: { type: 'raster', tiles: [tileUrl], tileSize: 256, attribution: '© OpenStreetMap contributors' } },
          layers: [{ id: 'osm', type: 'raster', source: 'osm' }],
        },
      })
      map.addControl(new NavigationControl({ showCompass: false }), 'top-right')
      map.addControl(new AttributionControl({ compact: true }), 'bottom-right')
      map.fitBounds([[bbox.west, bbox.south], [bbox.east, bbox.north]], { padding: 14, animate: false })
      map.on('moveend', () => {
        if (!map) return
        const bounds = map.getBounds()
        onViewportChange({ west: bounds.getWest(), south: bounds.getSouth(), east: bounds.getEast(), north: bounds.getNorth() }, map.getZoom())
      })
      mapRef.current = map
    }
    mount()
    const observer = typeof ResizeObserver === 'undefined' ? null : new ResizeObserver(mount)
    observer?.observe(element)
    return () => { observer?.disconnect(); map?.remove(); mapRef.current = null }
  }, [bbox.east, bbox.north, bbox.south, bbox.west, latitude, longitude, onViewportChange])

  useEffect(() => {
    const map = mapRef.current
    if (!map) return
    const center = map.getCenter()
    if (Math.abs(center.lng - longitude) > 0.01 || Math.abs(center.lat - latitude) > 0.01) {
      map.fitBounds([[bbox.west, bbox.south], [bbox.east, bbox.north]], { padding: 14, duration: 450 })
    }
  }, [bbox.east, bbox.north, bbox.south, bbox.west, latitude, longitude])

  return <div className="map-viewport" ref={container} aria-label="Interactive map viewport" />
}
