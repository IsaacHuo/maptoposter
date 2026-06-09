"""Map layer labels and conversion helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LayerDefinition:
    key: str
    en: str
    cn: str


LAYERS: tuple[LayerDefinition, ...] = (
    LayerDefinition("motorway", "Motorway", "高速公路"),
    LayerDefinition("primary", "Primary Roads", "主干道"),
    LayerDefinition("secondary", "Secondary Roads", "次干道"),
    LayerDefinition("water", "Water", "水域"),
    LayerDefinition("parks", "Parks", "公园"),
)

LAYER_KEYS = [layer.key for layer in LAYERS]
LAYERS_EN = [layer.en for layer in LAYERS]
LAYERS_CN = [layer.cn for layer in LAYERS]

_LABEL_TO_KEY = {
    label: layer.key
    for layer in LAYERS
    for label in (layer.en, layer.cn)
}
_KEY_TO_LABEL = {
    "en": {layer.key: layer.en for layer in LAYERS},
    "cn": {layer.key: layer.cn for layer in LAYERS},
}


def labels_for_language(lang: str) -> list[str]:
    """Return layer labels for a UI language code."""
    return LAYERS_EN if lang == "en" else LAYERS_CN


def selected_labels_to_keys(selected_labels: list[str] | tuple[str, ...] | None) -> list[str]:
    """Convert localized UI layer labels to stable layer keys."""
    if not selected_labels:
        return []
    return [_LABEL_TO_KEY[label] for label in selected_labels if label in _LABEL_TO_KEY]


def keys_to_labels(keys: list[str] | tuple[str, ...], lang: str) -> list[str]:
    """Convert stable layer keys to localized UI labels."""
    labels = _KEY_TO_LABEL["en" if lang == "en" else "cn"]
    return [labels[key] for key in keys if key in labels]


def selected_layer_flags(selected_labels: list[str] | tuple[str, ...] | None) -> dict[str, bool]:
    """Return render keyword flags for selected localized layer labels."""
    selected_keys = set(selected_labels_to_keys(selected_labels))
    return {
        "show_motorway": "motorway" in selected_keys,
        "show_primary": "primary" in selected_keys,
        "show_secondary": "secondary" in selected_keys,
        "show_water": "water" in selected_keys,
        "show_parks": "parks" in selected_keys,
    }

