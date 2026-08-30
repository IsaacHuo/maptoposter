export type LocationResult = {
  display_name: string
  latitude: number
  longitude: number
  country: string
  region: string
  country_code: string
  provider: string
}

export type BBox = {
  west: number
  south: number
  east: number
  north: number
}

export type StylePreset = {
  id: string
  name: string
  description: string
  preview: string
  background: string
  text: string
  water: string
  parks: string
  road_motorway: string
  road_primary: string
  road_secondary: string
  road_tertiary: string
  road_residential: string
  road_default: string
  gradient: string
}

export type Typography = {
  title: string
  subtitle: string
  caption: string
  coordinates: string
  font_family: string
  title_size: number
  subtitle_size: number
  caption_size: number
  coordinate_size: number
  letter_spacing: number
  line_height: number
  alignment: 'left' | 'center' | 'right'
  show_coordinates: boolean
  show_divider: boolean
}

export type LayerState = {
  motorway: boolean
  primary: boolean
  secondary: boolean
  residential: boolean
  water: boolean
  parks: boolean
}

export type PosterRequest = {
  location: LocationResult
  bbox: BBox
  distance_m: number
  zoom: number | null
  network_type: 'all' | 'drive' | 'walk' | 'bike'
  style_id: string
  colors: Record<string, string>
  typography: Typography
  layout: string
  layers: LayerState
  size: { preset: string; width_in?: number; height_in?: number }
}

export type PreviewPhase = 'idle' | 'preparing' | 'rendering' | 'success' | 'error'
