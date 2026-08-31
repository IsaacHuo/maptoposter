import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  Check, ChevronDown, ChevronRight, Download, Expand, Layers3, LayoutTemplate,
  LoaderCircle, MapPin, Minus, Move, Palette, Play, Plus, Redo2, Search, SlidersHorizontal,
  Type, Undo2, X,
} from 'lucide-react'
import { exportPoster, getStyles, prepareMap, renderPreview, searchPlaces } from './api'
import { MapViewport } from './components/MapViewport'
import type { BBox, LayerState, LocationResult, PosterRequest, PreviewPhase, StylePreset, Typography } from './types'
import './App.css'

const DEFAULT_LOCATION: LocationResult = {
  display_name: 'Beijing Forestry University', latitude: 40.0012, longitude: 116.3482,
  country: 'China', region: 'Beijing', country_code: 'cn', provider: 'default',
}
const DEFAULT_BBOX: BBox = { west: 116.292, south: 39.955, east: 116.405, north: 40.047 }
const DEFAULT_TYPE: Typography = {
  title: 'BEIJING FORESTRY UNIVERSITY', subtitle: 'BEIJING', caption: '', coordinates: '',
  font_family: 'auto', title_size: 46, subtitle_size: 17, caption_size: 13, coordinate_size: 11,
  letter_spacing: 0.08, line_height: 1.15, alignment: 'center', show_coordinates: true, show_divider: true,
}
const DEFAULT_LAYERS: LayerState = {
  motorway: true, primary: true, secondary: true, residential: true, water: true, parks: true,
}
const PANEL_IDS = ['location', 'style', 'layout', 'type', 'layers', 'size'] as const
type PanelId = typeof PANEL_IDS[number]
type Orientation = 'portrait' | 'landscape'
const SIZE_OPTIONS = [
  { id: '3:4', label: '3:4', aspect: 3 / 4, orientation: 'portrait' },
  { id: '4:5', label: '4:5', aspect: 4 / 5, orientation: 'portrait' },
  { id: '2:3', label: '2:3', aspect: 2 / 3, orientation: 'portrait' },
  { id: '9:16', label: '9:16', aspect: 9 / 16, orientation: 'portrait' },
  { id: 'A4', label: 'A4', aspect: 210 / 297, orientation: 'portrait' },
  { id: 'A3', label: 'A3', aspect: 297 / 420, orientation: 'portrait' },
  { id: '4:3', label: '4:3', aspect: 4 / 3, orientation: 'landscape' },
  { id: '5:4', label: '5:4', aspect: 5 / 4, orientation: 'landscape' },
  { id: '3:2', label: '3:2', aspect: 3 / 2, orientation: 'landscape' },
  { id: '16:9', label: '16:9', aspect: 16 / 9, orientation: 'landscape' },
  { id: 'A4-landscape', label: 'A4', aspect: 297 / 210, orientation: 'landscape' },
  { id: 'A3-landscape', label: 'A3', aspect: 420 / 297, orientation: 'landscape' },
  { id: '1:1', label: '1:1', aspect: 1, orientation: 'square' },
] as const
type PosterSizeId = typeof SIZE_OPTIONS[number]['id']
const ORIENTATION_PAIR: Partial<Record<PosterSizeId, PosterSizeId>> = {
  '3:4': '4:3', '4:3': '3:4', '4:5': '5:4', '5:4': '4:5', '2:3': '3:2', '3:2': '2:3',
  '9:16': '16:9', '16:9': '9:16', A4: 'A4-landscape', 'A4-landscape': 'A4', A3: 'A3-landscape', 'A3-landscape': 'A3',
}
const LAYOUT_OPTIONS = ['classic', 'editorial', 'minimal', 'bottom_left', 'centered']
const panelMeta = {
  location: ['Location', MapPin], style: ['Style', Palette], layout: ['Layout', LayoutTemplate],
  type: ['Type', Type], layers: ['Layers', Layers3], size: ['Size', SlidersHorizontal],
} as const

function extentFor(location: LocationResult): BBox {
  const latSpan = 0.09
  const lonSpan = latSpan / Math.max(Math.cos(location.latitude * Math.PI / 180), 0.25)
  return {
    west: Math.max(-179.999, location.longitude - lonSpan / 2), south: Math.max(-89.99, location.latitude - latSpan / 2),
    east: Math.min(179.999, location.longitude + lonSpan / 2), north: Math.min(89.99, location.latitude + latSpan / 2),
  }
}

function Section({ id, title, open, onToggle, children }: { id: PanelId; title: string; open: boolean; onToggle: () => void; children: React.ReactNode }) {
  return <section className={`editor-section editor-section-${id} ${open ? 'is-open' : ''}`}>
    <button className="section-heading" type="button" onClick={onToggle} aria-expanded={open}>
      <span>{title}</span>{open ? <ChevronDown size={17} /> : <ChevronRight size={17} />}
    </button>
    {open && <div className="section-content">{children}</div>}
  </section>
}

function ColorField({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return <label className="color-field">
    <span>{label}</span><span className="color-control"><input type="color" value={value} onChange={(event) => onChange(event.target.value)} /><code>{value.toUpperCase()}</code></span>
  </label>
}

function ProgressFeedback({ value, label, elapsed }: { value: number; label: string; elapsed: number }) {
  const rounded = Math.round(value)
  return <div className="progress-feedback">
    <div className="progress-meta"><span>{label}</span><span>{rounded}% · {elapsed}s</span></div>
    <div className="progress-track" role="progressbar" aria-label={label} aria-valuemin={0} aria-valuemax={100} aria-valuenow={rounded}>
      <span className="progress-fill" style={{ width: `${rounded}%` }} />
    </div>
  </div>
}

function GenerateControl({ phase, stale, disabled, onGenerate }: {
  phase: PreviewPhase
  stale: boolean
  disabled: boolean
  onGenerate: () => void
}) {
  const busy = phase === 'preparing' || phase === 'rendering'
  const label = phase === 'preparing'
    ? 'Fetching map data…'
    : phase === 'rendering'
      ? 'Rendering preview…'
      : stale
        ? 'Generate preview'
        : 'Generate again'
  return <div className="generate-footer">
    <button className="generate-button" type="button" onClick={onGenerate} disabled={disabled}>
      {busy ? <LoaderCircle className="spin" size={17} /> : <Play size={16} fill="currentColor" />}
      <span>{label}</span>
    </button>
    <small>Map data is fetched only after you start generation.</small>
  </div>
}

export default function App() {
  const [activePanel, setActivePanel] = useState<PanelId>('style')
  const [openPanels, setOpenPanels] = useState<Set<PanelId>>(new Set(['location', 'style', 'type']))
  const [location, setLocation] = useState(DEFAULT_LOCATION)
  const [bbox, setBBox] = useState(DEFAULT_BBOX)
  const [mapZoom, setMapZoom] = useState<number | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<LocationResult[]>([])
  const [searching, setSearching] = useState(false)
  const [styles, setStyles] = useState<StylePreset[]>([])
  const [styleId, setStyleId] = useState('japanese_ink')
  const [customColors, setCustomColors] = useState<Record<string, string>>({})
  const [typography, setTypography] = useState(DEFAULT_TYPE)
  const [layout, setLayout] = useState('classic')
  const [layers, setLayers] = useState(DEFAULT_LAYERS)
  const [orientation, setOrientation] = useState<Orientation>('portrait')
  const [size, setSize] = useState<PosterSizeId>('3:4')
  const [mapDataId, setMapDataId] = useState('')
  const [preparedSignature, setPreparedSignature] = useState('')
  const [renderedSignature, setRenderedSignature] = useState('')
  const [previewUrl, setPreviewUrl] = useState('/sample-poster.webp')
  const [previewPhase, setPreviewPhase] = useState<PreviewPhase>('idle')
  const [statusText, setStatusText] = useState('Adjust the settings, then generate a preview.')
  const [generationProgress, setGenerationProgress] = useState(0)
  const [generationElapsed, setGenerationElapsed] = useState(0)
  const [error, setError] = useState('')
  const [canvasZoom, setCanvasZoom] = useState(82)
  const [exportOpen, setExportOpen] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [exportProgress, setExportProgress] = useState(0)
  const [exportElapsed, setExportElapsed] = useState(0)
  const [exportStatus, setExportStatus] = useState('')
  const previewObjectUrl = useRef<string | null>(null)
  const generationController = useRef<AbortController | null>(null)
  const exportController = useRef<AbortController | null>(null)
  const generationStartedAt = useRef(0)
  const exportStartedAt = useRef(0)

  const selectedStyle = styles.find((style) => style.id === styleId)
  const effectiveColors = useMemo(() => selectedStyle ? {
    background: selectedStyle.background, text: selectedStyle.text, water: selectedStyle.water, parks: selectedStyle.parks,
    road_motorway: selectedStyle.road_motorway, road_primary: selectedStyle.road_primary,
    road_secondary: selectedStyle.road_secondary, road_tertiary: selectedStyle.road_tertiary,
    road_residential: selectedStyle.road_residential, road_default: selectedStyle.road_default,
    gradient: selectedStyle.gradient, ...customColors,
  } : customColors, [customColors, selectedStyle])

  const poster = useMemo<PosterRequest>(() => ({
    location, bbox, distance_m: 10_000, zoom: mapZoom, network_type: 'all', style_id: styleId,
    colors: customColors, typography, layout, layers, size: { preset: size },
  }), [bbox, customColors, layers, layout, location, mapZoom, size, styleId, typography])
  const posterSignature = useMemo(() => JSON.stringify(poster), [poster])
  const dataSignature = useMemo(() => JSON.stringify({ location, bbox, network: poster.network_type, layout, size }), [bbox, layout, location, poster.network_type, size])
  const prepareRequest = useMemo(() => ({
    location, bbox, distance_m: 10_000, zoom: mapZoom, network_type: 'all' as const,
    style_id: 'japanese_ink', colors: {}, typography: DEFAULT_TYPE, layout, layers: DEFAULT_LAYERS, size: { preset: size },
  }), [bbox, layout, location, mapZoom, size])
  const sizeOption = SIZE_OPTIONS.find((option) => option.id === size) ?? SIZE_OPTIONS[0]
  const posterAspect = sizeOption.aspect
  const visibleSizeOptions = SIZE_OPTIONS.filter((option) => option.orientation === orientation || option.orientation === 'square')
  const isGenerating = previewPhase === 'preparing' || previewPhase === 'rendering'
  const previewStale = renderedSignature !== posterSignature

  useEffect(() => {
    const controller = new AbortController()
    getStyles(controller.signal).then((items) => {
      setStyles(items)
      setStyleId((current) => items.some((item) => item.id === current) ? current : items[0]?.id ?? current)
    }).catch((reason: Error) => { if (reason.name !== 'AbortError') setError(reason.message) })
    return () => controller.abort()
  }, [])

  useEffect(() => {
    if (!isGenerating) return
    const timer = window.setInterval(() => {
      setGenerationElapsed(Math.floor((Date.now() - generationStartedAt.current) / 1000))
      setGenerationProgress((current) => {
        const ceiling = previewPhase === 'preparing' ? 58 : 94
        return Math.min(ceiling, current + Math.max(0.6, (ceiling - current) * 0.04))
      })
    }, 400)
    return () => window.clearInterval(timer)
  }, [isGenerating, previewPhase])

  useEffect(() => {
    if (!exporting) return
    const timer = window.setInterval(() => {
      setExportElapsed(Math.floor((Date.now() - exportStartedAt.current) / 1000))
      setExportProgress((current) => Math.min(94, current + Math.max(0.6, (94 - current) * 0.04)))
    }, 400)
    return () => window.clearInterval(timer)
  }, [exporting])

  useEffect(() => () => {
    generationController.current?.abort()
    exportController.current?.abort()
    if (previewObjectUrl.current) URL.revokeObjectURL(previewObjectUrl.current)
  }, [])

  const runSearch = async (event: React.FormEvent) => {
    event.preventDefault()
    const query = searchQuery.trim()
    if (!query) return
    setSearching(true); setError('')
    try { setSearchResults(await searchPlaces(query)) }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Search failed') }
    finally { setSearching(false) }
  }

  const chooseLocation = (result: LocationResult) => {
    setLocation(result); setBBox(extentFor(result)); setMapZoom(null); setSearchResults([]); setSearchQuery('')
    const title = result.display_name.split(',')[0]?.trim() || result.display_name
    setTypography((current) => ({ ...current, title, subtitle: result.region || result.country, caption: '' }))
  }

  const changeOrientation = (next: Orientation) => {
    if (next === orientation) return
    setOrientation(next)
    setSize((current) => current === '1:1' ? current : ORIENTATION_PAIR[current] ?? (next === 'portrait' ? '3:4' : '4:3'))
  }

  const updateColor = (key: string, value: string) => setCustomColors((current) => ({ ...current, [key]: value }))
  const togglePanel = (id: PanelId) => {
    setActivePanel(id)
    setOpenPanels((current) => { const next = new Set(current); if (next.has(id)) next.delete(id); else next.add(id); return next })
  }
  const updateViewport = useCallback((nextBBox: BBox, zoom: number) => {
    const rounded = Object.fromEntries(Object.entries(nextBBox).map(([key, value]) => [key, Number(value.toFixed(6))])) as BBox
    setBBox((current) => {
      const unchanged = (Object.keys(rounded) as (keyof BBox)[]).every((key) => Math.abs(current[key] - rounded[key]) < 0.00001)
      return unchanged ? current : rounded
    })
    setMapZoom((current) => current !== null && Math.abs(current - zoom) < 0.01 ? current : Number(zoom.toFixed(2)))
  }, [])

  const runGeneration = async () => {
    const requestPoster = poster
    const requestPosterSignature = posterSignature
    const requestDataSignature = dataSignature
    const controller = new AbortController()
    generationController.current?.abort()
    generationController.current = controller
    generationStartedAt.current = Date.now()
    setGenerationElapsed(0); setGenerationProgress(4); setPreviewPhase('preparing')
    setStatusText('Fetching streets, water, and parks…'); setError('')
    try {
      let currentMapDataId = mapDataId
      if (!currentMapDataId || preparedSignature !== requestDataSignature) {
        const result = await prepareMap(prepareRequest, controller.signal)
        currentMapDataId = result.map_data_id
        setMapDataId(currentMapDataId); setPreparedSignature(requestDataSignature)
        setStatusText(result.cache_hit ? 'Map data loaded from cache. Rendering preview…' : 'Map data ready. Rendering preview…')
      } else {
        setStatusText('Using prepared map data. Rendering preview…')
      }
      setGenerationProgress(68); setPreviewPhase('rendering')
      const blob = await renderPreview(currentMapDataId, requestPoster, controller.signal)
      if (previewObjectUrl.current) URL.revokeObjectURL(previewObjectUrl.current)
      const url = URL.createObjectURL(blob)
      previewObjectUrl.current = url
      setPreviewUrl(url); setRenderedSignature(requestPosterSignature); setGenerationProgress(100); setPreviewPhase('success')
      setStatusText(`Preview ready in ${((Date.now() - generationStartedAt.current) / 1000).toFixed(1)}s`)
    } catch (reason) {
      if (reason instanceof Error && reason.name === 'AbortError') return
      setPreviewPhase('error'); setError(reason instanceof Error ? reason.message : 'Preview failed')
      setStatusText('Could not generate the preview')
    } finally {
      if (generationController.current === controller) generationController.current = null
    }
  }

  const download = async (format: 'png' | 'svg' | 'pdf', dpi: number) => {
    if (!mapDataId || preparedSignature !== dataSignature) { setError('Wait for the map data to finish loading before export.'); return }
    const controller = new AbortController()
    exportController.current?.abort()
    exportController.current = controller
    exportStartedAt.current = Date.now()
    setExporting(true); setExportProgress(5); setExportElapsed(0); setExportOpen(false); setError('')
    setExportStatus(`Rendering ${format.toUpperCase()} at ${dpi} DPI…`)
    try {
      const result = await exportPoster(mapDataId, poster, format, dpi, controller.signal)
      setExportProgress(100)
      const url = URL.createObjectURL(result.blob)
      const link = document.createElement('a'); link.href = url; link.download = result.filename; link.click()
      window.setTimeout(() => URL.revokeObjectURL(url), 1000)
      setStatusText(`${format.toUpperCase()} downloaded in ${((Date.now() - exportStartedAt.current) / 1000).toFixed(1)}s`)
    } catch (reason) {
      if (!(reason instanceof Error && reason.name === 'AbortError')) setError(reason instanceof Error ? reason.message : 'Export failed')
    } finally {
      if (exportController.current === controller) exportController.current = null
      setExporting(false)
    }
  }

  const panelContent: Record<PanelId, React.ReactNode> = {
    location: <>
      <form className="search-box" onSubmit={runSearch}>
        <Search size={16} /><input value={searchQuery} onChange={(event) => setSearchQuery(event.target.value)} placeholder="Search a place…" aria-label="Search a place" />
        {searchQuery && <button type="button" className="icon-button" onClick={() => { setSearchQuery(''); setSearchResults([]) }} aria-label="Clear search"><X size={15} /></button>}
        <button className="search-submit" type="submit" disabled={searching}>{searching ? <LoaderCircle className="spin" size={15} /> : 'Search'}</button>
      </form>
      {searchResults.length > 0 && <div className="search-results">{searchResults.map((result) => <button key={`${result.latitude}-${result.longitude}-${result.display_name}`} onClick={() => chooseLocation(result)}>
        <MapPin size={15} /><span><strong>{result.display_name}</strong><small>{[result.region, result.country].filter(Boolean).join(', ')}</small></span>
      </button>)}</div>}
      <div className="selected-place"><span className="pin"><MapPin size={17} /></span><span><strong>{location.display_name}</strong><small>{location.latitude.toFixed(4)}° / {location.longitude.toFixed(4)}°</small></span></div>
      <MapViewport longitude={location.longitude} latitude={location.latitude} bbox={bbox} onViewportChange={updateViewport} />
      <p className="field-help">Drag or zoom to set the exact area used by the poster.</p>
    </>,
    style: <>
      <div className="style-grid">{styles.slice(0, 6).map((style) => <button key={style.id} className={`style-card ${style.id === styleId ? 'is-selected' : ''}`} onClick={() => { setStyleId(style.id); setCustomColors({}) }} title={style.description}>
        <span className="style-preview" style={{ backgroundColor: style.background, color: style.road_primary }}>{style.preview && <img src={style.preview} alt="" onError={(event) => { event.currentTarget.style.display = 'none' }} />}<i /><i /><i /></span>
        <span>{style.name}</span>{style.id === styleId && <b><Check size={12} /></b>}
      </button>)}</div>
      {styles.length > 6 && <label className="field"><span>More styles</span><select value={styleId} onChange={(event) => { setStyleId(event.target.value); setCustomColors({}) }}>{styles.map((style) => <option key={style.id} value={style.id}>{style.name}</option>)}</select></label>}
      <div className="subheading"><span>Customize</span>{Object.keys(customColors).length > 0 && <button onClick={() => setCustomColors({})}>Reset</button>}</div>
      <div className="color-list">
        <ColorField label="Background" value={effectiveColors.background ?? '#ffffff'} onChange={(value) => updateColor('background', value)} />
        <ColorField label="Text" value={effectiveColors.text ?? '#17191d'} onChange={(value) => updateColor('text', value)} />
        <ColorField label="Water" value={effectiveColors.water ?? '#c9c6bf'} onChange={(value) => updateColor('water', value)} />
        <ColorField label="Parks" value={effectiveColors.parks ?? '#eae7e1'} onChange={(value) => updateColor('parks', value)} />
        <ColorField label="Major roads" value={effectiveColors.road_primary ?? '#222222'} onChange={(value) => updateColor('road_primary', value)} />
        <ColorField label="Minor roads" value={effectiveColors.road_residential ?? '#777777'} onChange={(value) => updateColor('road_residential', value)} />
      </div>
    </>,
    layout: <div className="choice-grid">{LAYOUT_OPTIONS.map((value) => <button key={value} className={layout === value ? 'is-selected' : ''} onClick={() => setLayout(value)}><span className={`layout-glyph ${value}`} /><strong>{value.replace('_', ' ')}</strong></button>)}</div>,
    type: <div className="form-stack">
      <label className="field"><span>Title</span><input value={typography.title} onChange={(event) => setTypography({ ...typography, title: event.target.value })} /></label>
      <label className="field"><span>Subtitle</span><input value={typography.subtitle} onChange={(event) => setTypography({ ...typography, subtitle: event.target.value })} /></label>
      <div className="two-fields"><label className="field"><span>Title size</span><input type="number" min="12" max="120" value={typography.title_size} onChange={(event) => setTypography({ ...typography, title_size: Number(event.target.value) })} /></label><label className="field"><span>Alignment</span><select value={typography.alignment} onChange={(event) => setTypography({ ...typography, alignment: event.target.value as Typography['alignment'] })}><option>left</option><option>center</option><option>right</option></select></label></div>
      <label className="range-field"><span>Letter spacing <output>{Math.round(typography.letter_spacing * 100)}%</output></span><input type="range" min="0" max="0.3" step="0.01" value={typography.letter_spacing} onChange={(event) => setTypography({ ...typography, letter_spacing: Number(event.target.value) })} /></label>
      <label className="check-field"><input type="checkbox" checked={typography.show_coordinates} onChange={(event) => setTypography({ ...typography, show_coordinates: event.target.checked })} />Show coordinates</label>
      <label className="check-field"><input type="checkbox" checked={typography.show_divider} onChange={(event) => setTypography({ ...typography, show_divider: event.target.checked })} />Show divider</label>
    </div>,
    layers: <div className="toggle-list">{Object.entries(layers).map(([key, value]) => <label key={key}><span>{key.replace('_', ' ')}</span><input type="checkbox" checked={value} onChange={(event) => setLayers({ ...layers, [key]: event.target.checked })} /></label>)}</div>,
    size: <>
      <div className="orientation-toggle" role="group" aria-label="Poster orientation">
        <button type="button" className={orientation === 'portrait' ? 'is-selected' : ''} aria-pressed={orientation === 'portrait'} onClick={() => changeOrientation('portrait')}>Portrait</button>
        <button type="button" className={orientation === 'landscape' ? 'is-selected' : ''} aria-pressed={orientation === 'landscape'} onClick={() => changeOrientation('landscape')}>Landscape</button>
      </div>
      <div className="size-grid">{visibleSizeOptions.map((option) => <button key={option.id} aria-label={`${orientation} ${option.label}`} className={size === option.id ? 'is-selected' : ''} onClick={() => setSize(option.id)}><span className="size-shape" style={{ aspectRatio: String(option.aspect) }} />{option.label}</button>)}</div>
      <p className="field-help">The selected map area is expanded to fit the poster without cropping. Export uses this ratio and DPI.</p>
    </>,
  }

  return <div className="app-shell">
    <header className="topbar">
      <a className="brand" href="/">MapToPoster</a>
      <div className="topbar-tools"><button className="desktop-only icon-button" disabled aria-label="Undo"><Undo2 size={18} /></button><button className="desktop-only icon-button" disabled aria-label="Redo"><Redo2 size={18} /></button><button className="desktop-only quiet-button"><Layers3 size={17} /> Layers</button>
        <div className="export-group"><button className="export-primary" onClick={() => download('png', 300)} disabled={exporting || isGenerating}>{exporting ? <LoaderCircle className="spin" size={16} /> : <Download size={16} />}<span>{exporting ? `${Math.round(exportProgress)}%` : 'Export'}</span></button><button className="export-toggle" onClick={() => setExportOpen(!exportOpen)} disabled={exporting || isGenerating} aria-label="Export options"><ChevronDown size={15} /></button>
          {exportOpen && <div className="export-menu"><button onClick={() => download('png', 150)}>PNG · Preview</button><button onClick={() => download('png', 300)}>PNG · Print 300 DPI</button><button onClick={() => download('svg', 300)}>SVG · Vector</button><button onClick={() => download('pdf', 300)}>PDF · Print</button></div>}
        </div>
      </div>
    </header>

    <aside className="sidebar">
      {PANEL_IDS.map((id) => <Section key={id} id={id} title={panelMeta[id][0]} open={openPanels.has(id)} onToggle={() => togglePanel(id)}>{panelContent[id]}</Section>)}
      <GenerateControl phase={previewPhase} stale={previewStale} disabled={isGenerating || exporting} onGenerate={runGeneration} />
    </aside>

    <nav className="mobile-tabs" aria-label="Editor panels">{PANEL_IDS.map((id) => { const Icon = panelMeta[id][1]; return <button key={id} className={activePanel === id ? 'is-active' : ''} onClick={() => setActivePanel(id)}><Icon size={19} /><span>{panelMeta[id][0]}</span></button> })}</nav>
    <section className="mobile-sheet"><div className="mobile-sheet-heading"><strong>{panelMeta[activePanel][0]}</strong><span>Poster settings</span></div>{panelContent[activePanel]}<GenerateControl phase={previewPhase} stale={previewStale} disabled={isGenerating || exporting} onGenerate={runGeneration} /></section>

    <main className="workspace">
      <div className="canvas-stage">
        <div className={`poster-frame ${posterAspect >= 1 ? 'is-wide' : 'is-tall'}`} style={{ transform: `scale(${canvasZoom / 100})`, aspectRatio: String(posterAspect) }}>
          <img src={previewUrl} alt={`Poster preview for ${location.display_name}`} />
          {isGenerating && <div className="preview-loading"><LoaderCircle className="spin" /><ProgressFeedback value={generationProgress} label={statusText} elapsed={generationElapsed} /></div>}
        </div>
      </div>
      <div className={`preview-status ${error ? 'error' : previewPhase}`} role="status">
        <div className="preview-status-copy">{exporting || isGenerating ? <LoaderCircle className="spin" size={15} /> : previewPhase === 'success' && !previewStale ? <Check size={15} /> : previewPhase === 'error' ? <X size={15} /> : <Play size={13} />}<span>{exporting ? exportStatus : error || (previewPhase === 'success' && previewStale ? 'Settings changed. Generate again to update the preview.' : statusText)}</span></div>
        {exporting ? <ProgressFeedback value={exportProgress} label={exportStatus} elapsed={exportElapsed} /> : isGenerating ? <ProgressFeedback value={generationProgress} label={statusText} elapsed={generationElapsed} /> : null}
      </div>
      <div className="canvas-toolbar"><div className="tool-group"><button aria-label="Pan"><Move size={17} /></button><button aria-label="Fit canvas" onClick={() => setCanvasZoom(82)}><Expand size={17} /></button></div><div className="tool-group zoom-controls"><button onClick={() => setCanvasZoom((value) => Math.max(35, value - 10))} aria-label="Zoom out"><Minus size={16} /></button><output>{canvasZoom}%</output><button onClick={() => setCanvasZoom((value) => Math.min(140, value + 10))} aria-label="Zoom in"><Plus size={16} /></button></div><button className="fit-button" onClick={() => setCanvasZoom(82)}>Fit</button></div>
    </main>
  </div>
}
