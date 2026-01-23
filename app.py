# -*- coding: utf-8 -*-
"""
Gradio Web Interface for City Map Poster Generator
"""

import os
import json
import gradio as gr

# Import from the main module
from cities_data import (
    get_countries,
    get_provinces,
    get_cities,
    get_districts,
    translate,
    get_country_key,
)


# --- Constants ---
THEMES_DIR = "themes"
FONTS_DIR = "fonts"
POSTERS_DIR = "posters"

# Layer Constants
LAYERS_EN = ["Motorway", "Primary Roads", "Secondary Roads", "Water", "Parks"]
LAYERS_CN = ["高速公路", "主干道", "次干道", "水域", "公园"]
LAYER_KEYS = ["motorway", "primary", "secondary", "water", "parks"]


def get_available_themes():
    """Scans the themes directory and returns a list of available theme names."""
    if not os.path.exists(THEMES_DIR):
        return []

    themes = []
    for file in sorted(os.listdir(THEMES_DIR)):
        if file.endswith(".json"):
            theme_name = file[:-5]
            themes.append(theme_name)
    return themes


def get_theme_choices(lang="en"):
    """Return a list of (Display Name, Internal Name) tuples for themes."""
    internal_names = get_available_themes()
    choices = []

    for internal_name in internal_names:
        theme_info = load_theme_info(internal_name)
        if theme_info:
            proper_name = theme_info.get("name", internal_name)
            display_name = translate(proper_name, lang)
            choices.append((display_name, internal_name))
        else:
            choices.append((internal_name, internal_name))

    return choices


def load_theme_info(theme_name):
    """Load theme details for preview."""
    theme_file = os.path.join(THEMES_DIR, f"{theme_name}.json")
    if os.path.exists(theme_file):
        with open(theme_file, "r") as f:
            return json.load(f)
    return None


def get_theme_preview_html(theme_name, lang="en"):
    """Generate HTML preview for a theme."""
    theme = load_theme_info(theme_name)
    lang_code = "en" if lang == "English" else "cn"

    if not theme:
        return f"<p>{'Theme load failed' if lang_code == 'en' else '主题加载失败'}</p>"

    # Translated labels
    labels = {
        "bg": "Background" if lang_code == "en" else "背景",
        "text": "Text" if lang_code == "en" else "文字",
        "motorway": "Motorway" if lang_code == "en" else "高速公路",
        "primary": "Primary Road" if lang_code == "en" else "主干道",
        "secondary": "Secondary Road" if lang_code == "en" else "次干道",
        "water": "Water" if lang_code == "en" else "水域",
        "parks": "Parks" if lang_code == "en" else "公园",
    }

    # Create color swatches
    colors = [
        (labels["bg"], theme.get("bg", "#FFFFFF")),
        (labels["text"], theme.get("text", "#000000")),
        (labels["motorway"], theme.get("road_motorway", "#000000")),
        (labels["primary"], theme.get("road_primary", "#333333")),
        (labels["secondary"], theme.get("road_secondary", "#666666")),
        (labels["water"], theme.get("water", "#C0C0C0")),
        (labels["parks"], theme.get("parks", "#F0F0F0")),
    ]

    display_name = translate(theme.get("name", theme_name), lang_code)
    description = theme.get("description", "")
    # Optional: translate description if we really want to, but might be too much work

    html = f"""
    <div style="padding: 12px; background: {theme.get("bg", "#FFFFFF")}; border-radius: 8px; border: 1px solid #ddd;">
        <h4 style="color: {theme.get("text", "#000000")}; margin: 0 0 8px 0; font-size: 14px;">
            {display_name}
        </h4>
        <p style="color: {theme.get("text", "#000000")}; opacity: 0.7; margin: 0 0 12px 0; font-size: 12px;">
            {description}
        </p>
        <div style="display: flex; flex-wrap: wrap; gap: 6px;">
    """

    for label, color in colors:
        html += f"""
            <div style="display: flex; align-items: center; gap: 4px;">
                <div style="width: 20px; height: 20px; background: {color}; border-radius: 4px; border: 1px solid #ccc;"></div>
                <span style="font-size: 10px; color: {theme.get("text", "#000")}; opacity: 0.8;">{label}</span>
            </div>
        """

    html += "</div></div>"
    return html


def generate_poster(
    country_display,
    province,
    city_dropdown,
    district_dropdown,
    theme_name,
    distance,
    width,
    height,
    output_format,
    no_crop,
    poster_lang,
    layers_selection,
    progress=gr.Progress(),
):
    """
    Generate the map poster with given parameters.
    """
    # Import here to avoid circular imports and ensure THEME is set correctly
    import create_map_poster as cmp

    # Decode layer selection
    show_motorway = any(x in ["Motorway", "高速公路"] for x in layers_selection)
    show_primary = any(x in ["Primary Roads", "主干道"] for x in layers_selection)
    show_secondary = any(x in ["Secondary Roads", "次干道"] for x in layers_selection)
    show_water = any(x in ["Water", "水域"] for x in layers_selection)
    show_parks = any(x in ["Parks", "公园"] for x in layers_selection)

    # Parse country
    # Since we now use (Display, Value) tuples where Value is the key,
    # country_display is likely already the key. get_country_key remains for safety.
    selected_country = get_country_key(country_display)

    # Use dropdown selection
    # If district is selected and isn't "整个城市", use its coordinates
    selected_location = (
        district_dropdown
        if (district_dropdown and district_dropdown != city_dropdown)
        else city_dropdown
    )

    if not selected_location:
        return None, "❌ 请选择城市或区县名称"

    if not selected_country:
        return None, "❌ 请选择国家"

    # Determine display names based on poster_lang
    lang_code = "en" if poster_lang == "English" else "cn"
    display_city = translate(selected_location, lang_code)
    display_country = translate(selected_country, lang_code)

    progress(0.1, desc="正在加载主题...")

    # Load theme
    cmp.THEME = cmp.load_theme(theme_name)

    progress(0.2, desc="正在获取坐标...")

    try:
        # We search coordinates using the selection
        # CMP might need the "original" names if OSM behaves better with them
        # For China, "广州" is better than "Guangzhou" for geopy sometimes, but geopy is usually good.
        # Let's ensure we use the 'original' internal key if possible for best OSM matching
        # However, for cities, we don't have a strict key map like for countries.
        # We can try to translate to CN if it's a Chinese city.
        search_city = selected_location
        search_country = selected_country
        # Use city as parent if searching for a district, otherwise use province
        search_parent = (
            city_dropdown
            if (district_dropdown and district_dropdown != city_dropdown)
            else province
        )

        coords = cmp.get_coordinates(search_city, search_country, parent=search_parent)
    except Exception as e:
        return None, f"❌ 无法找到城市坐标: {str(e)}"

    progress(0.3, desc="正在生成海报...")

    # Generate output filename (using English/Slugified names)
    en_city = translate(selected_location, "en")
    output_file = cmp.generate_output_filename(en_city, theme_name, output_format)

    try:
        # Wrap the generator to yield status updates and final result
        for status in cmp.create_poster(
            display_city,  # Pass translated names for display
            display_country,
            coords,
            distance,
            output_file,
            output_format,
            width=width,
            height=height,
            no_crop=no_crop,
            show_motorway=show_motorway,
            show_primary=show_primary,
            show_secondary=show_secondary,
            show_water=show_water,
            show_parks=show_parks,
        ):
            # Translate common status messages if possible
            status_display = status
            if lang_code == "cn":
                if "Downloading street network" in status:
                    status_display = "正在下载街道数据..."
                elif "Downloading features" in status:
                    status_display = "正在下载水域和公园数据..."
                elif "Rendering map" in status:
                    status_display = "正在渲染地图..."
                elif "Applying road styles" in status:
                    status_display = "正在应用样式..."
                elif "Saving to" in status:
                    status_display = "正在保存海报..."
                elif "Done" in status:
                    status_display = "完成！"

            yield None, f"⏳ {status_display}"

        progress(1.0, desc="完成!")

        yield output_file, f"✅ 海报生成成功！保存至: {output_file}"

    except Exception as e:
        import traceback

        traceback.print_exc()
        yield None, f"❌ 生成失败: {str(e)}"


def update_provinces(country, lang="en"):
    """Update province dropdown based on country selection and language."""
    # country is the internal key
    lang_code = "en" if lang == "English" else "cn"
    provinces = get_provinces(country, lang_code)
    if provinces:
        return gr.update(choices=provinces, value=provinces[0][1], visible=True)
    return gr.update(choices=[], value=None, visible=False)


def update_cities(country, province, lang="en"):
    """Update city dropdown based on province selection and language."""
    # country and province are internal keys
    lang_code = "en" if lang == "English" else "cn"
    cities = get_cities(country, province, lang_code)
    if cities:
        # For China, if it's a municipality, get_cities returns [province_name]
        # We should automatically trigger update_districts then.
        return gr.update(choices=cities, value=cities[0][1])
    return gr.update(choices=[], value=None)


def update_districts(country, province, city, lang="en"):
    """Update district dropdown based on city selection."""
    if country != "中国":
        return gr.update(choices=[], value=None, visible=False)

    lang_code = "en" if lang == "English" else "cn"
    districts = get_districts(country, province, city, lang_code)
    if districts:
        return gr.update(choices=districts, value=districts[0][1], visible=True)
    return gr.update(choices=[], value=None, visible=False)


def on_theme_change(theme_name, lang="en"):
    """Update theme preview when theme changes."""
    return get_theme_preview_html(theme_name, lang)


# --- Build Gradio Interface ---
def create_interface():
    """Create and return the Gradio interface."""

    # Get initial data (Default English)
    default_lang_code = "en"
    default_lang_radio = "English"
    countries = get_countries(default_lang_code)
    theme_choices = get_theme_choices(default_lang_code)

    default_country_key = "中国"
    default_provinces = get_provinces(default_country_key, default_lang_code)
    default_province_key = default_provinces[0][1] if default_provinces else None
    default_cities = (
        get_cities(default_country_key, default_province_key, default_lang_code)
        if default_province_key
        else []
    )
    default_city_key = default_cities[0][1] if default_cities else None
    default_theme = theme_choices[0][1] if theme_choices else "feature_based"
    default_theme = theme_choices[0][1] if theme_choices else "feature_based"

    with gr.Blocks(
        title="城市地图海报生成器",
    ) as demo:
        # Header
        gr.HTML("""
            <div class="header-title">城市地图海报生成器</div>
            <div class="header-subtitle">选择任意城市，自定义主题风格，生成精美地图海报</div>
            
            <div style="max-width: 800px; margin: 0 auto 20px auto; padding: 12px; background: #fff5f5; border: 1px solid #feb2b2; border-radius: 8px; text-align: left; font-size: 13px; line-height: 1.6; color: #c53030;">
                <b>⚠️ 注意：</b><br>
                • <b>特大城市</b>（如北京）：中心定位可能不准。<br>
                • <b>小城市</b>：由于 OpenStreetMap 数据缺失，部分图层（如公园/水域）可能无法显示。<br>
                • <b>生成速度</b>：使用国外服务器数据且渲染逻辑较基础，下载和生成速度可能较慢。<br>
                • <b>数据来源</b>：© OpenStreetMap contributors
            </div>
        """)

        with gr.Row():
            # Left Column - Controls
            with gr.Column(scale=1):
                # City Selection Section
                gr.HTML('<div class="section-title">📍 城市选择</div>')

                lang_radio = gr.Radio(
                    choices=["English", "Chinese"],
                    value="English",
                    label="海报语言",
                    info="选择海报及界面的显示语言",
                )

                country_dropdown = gr.Dropdown(
                    choices=countries,
                    value=default_country_key,
                    label="选择国家",
                    interactive=True,
                )

                province_dropdown = gr.Dropdown(
                    choices=default_provinces,
                    value=default_province_key,
                    label="选择省份/州",
                    interactive=True,
                )

                city_dropdown = gr.Dropdown(
                    choices=default_cities,
                    value=default_city_key,
                    label="选择城市",
                    interactive=True,
                )

                district_dropdown = gr.Dropdown(
                    choices=get_districts(
                        default_country_key,
                        default_province_key,
                        default_city_key,
                        default_lang_code,
                    ),
                    value=default_city_key,
                    label="选择区县",
                    interactive=True,
                    visible=(default_country_key == "中国"),
                )

                gr.HTML("<hr style='margin: 20px 0; border-color: #eee;'>")

                # Theme Section
                gr.HTML('<div class="section-title">🎨 主题风格</div>')

                theme_dropdown = gr.Dropdown(
                    choices=theme_choices,
                    value=default_theme,
                    label="选择主题",
                    interactive=True,
                )

                theme_preview = gr.HTML(
                    value=get_theme_preview_html(default_theme, default_lang_radio),
                    label="主题预览",
                )

                gr.HTML("<hr style='margin: 20px 0; border-color: #eee;'>")

                # Parameters Section
                gr.HTML('<div class="section-title">⚙️ 参数设置</div>')

                distance_slider = gr.Slider(
                    minimum=4000,
                    maximum=30000,
                    value=10000,
                    step=1000,
                    label="地图范围 (米)",
                    info="4000-6000: 小城区 | 8000-12000: 中等城市 | 15000+: 大都市 (范围越大生成越慢)",
                )

                with gr.Row():
                    width_input = gr.Number(
                        value=12.0, label="宽度 (英寸)", minimum=6, maximum=24
                    )
                    height_input = gr.Number(
                        value=16.0, label="高度 (英寸)", minimum=8, maximum=32
                    )

                format_radio = gr.Radio(
                    choices=["png", "svg", "pdf"],
                    value="png",
                    label="输出格式",
                    info="PNG: 适合打印 | SVG: 矢量图 | PDF: 文档",
                )

                no_crop_checkbox = gr.Checkbox(
                    value=False,
                    label="保留边距 (不裁剪)",
                    info="勾选后保留海报边缘背景",
                )

                layers_checkbox = gr.CheckboxGroup(
                    choices=LAYERS_EN,
                    value=LAYERS_EN,
                    label="图层显示",
                    info="选择需要显示的地图元素",
                )

                # Generate Button
                generate_btn = gr.Button("🚀 生成海报", variant="primary", size="lg")

            # Right Column - Output
            with gr.Column(scale=1):
                gr.HTML('<div class="section-title">🖼️ 生成结果</div>')

                output_image = gr.Image(
                    label="海报预览",
                    type="filepath",
                    elem_classes=["output-image"],
                    height=600,
                    interactive=False,
                )

                output_status = gr.Textbox(label="状态", interactive=False)

                download_btn = gr.DownloadButton(label="📥 下载海报", visible=False)

        # --- Event Handlers ---

        # Language change -> update all dropdowns
        def on_lang_change(
            lang,
            current_country,
            current_province,
            current_city,
            current_theme,
            current_layers,
        ):
            lang_code = "en" if lang == "English" else "cn"
            new_countries = get_countries(lang_code)

            # Use keys to maintain selection
            new_provinces = get_provinces(current_country, lang_code)
            new_cities = (
                get_cities(current_country, current_province, lang_code)
                if current_province
                else []
            )
            new_districts = (
                get_districts(
                    current_country, current_province, current_city, lang_code
                )
                if current_city
                else []
            )

            # Themes
            new_theme_choices = get_theme_choices(lang_code)
            new_preview = get_theme_preview_html(current_theme, lang)

            # Layers
            map_en_to_key = dict(zip(LAYERS_EN, LAYER_KEYS))
            map_cn_to_key = dict(zip(LAYERS_CN, LAYER_KEYS))
            map_key_to_en = dict(zip(LAYER_KEYS, LAYERS_EN))
            map_key_to_cn = dict(zip(LAYER_KEYS, LAYERS_CN))

            current_keys = []
            for x in current_layers:
                if x in map_en_to_key:
                    current_keys.append(map_en_to_key[x])
                elif x in map_cn_to_key:
                    current_keys.append(map_cn_to_key[x])

            target_map = map_key_to_en if lang == "English" else map_key_to_cn
            new_layer_choices = LAYERS_EN if lang == "English" else LAYERS_CN
            new_layer_values = [target_map[k] for k in current_keys if k in target_map]

            return (
                gr.update(choices=new_countries, value=current_country),
                gr.update(choices=new_provinces, value=current_province),
                gr.update(choices=new_cities, value=current_city),
                gr.update(
                    choices=new_districts,
                    value=current_city if current_city else None,
                    visible=(current_country == "中国"),
                ),
                gr.update(choices=new_theme_choices),
                new_preview,
                gr.update(
                    choices=new_layer_choices,
                    value=new_layer_values,
                    label="Layers" if lang == "English" else "图层显示",
                ),
            )

        lang_radio.change(
            fn=on_lang_change,
            inputs=[
                lang_radio,
                country_dropdown,
                province_dropdown,
                city_dropdown,
                theme_dropdown,
                layers_checkbox,
            ],
            outputs=[
                country_dropdown,
                province_dropdown,
                city_dropdown,
                district_dropdown,
                theme_dropdown,
                theme_preview,
                layers_checkbox,
            ],
        )

        # Country change -> update provinces
        country_dropdown.change(
            fn=update_provinces,
            inputs=[country_dropdown, lang_radio],
            outputs=[province_dropdown],
        )

        # Province change -> update cities
        province_dropdown.change(
            fn=update_cities,
            inputs=[country_dropdown, province_dropdown, lang_radio],
            outputs=[city_dropdown],
        ).then(  # Update districts after city changes
            fn=update_districts,
            inputs=[country_dropdown, province_dropdown, city_dropdown, lang_radio],
            outputs=[district_dropdown],
        )

        # City change -> update districts
        city_dropdown.change(
            fn=update_districts,
            inputs=[country_dropdown, province_dropdown, city_dropdown, lang_radio],
            outputs=[district_dropdown],
        )

        # Theme change -> update preview
        theme_dropdown.change(
            fn=on_theme_change,
            inputs=[theme_dropdown, lang_radio],
            outputs=[theme_preview],
        )

        # Generate button click
        def on_generate_complete(filepath, status):
            """Handle generate completion - show download button if successful."""
            if filepath and os.path.exists(filepath):
                return filepath, status, gr.update(visible=True, value=filepath)
            return filepath, status, gr.update(visible=False)

        generate_btn.click(
            fn=generate_poster,
            inputs=[
                country_dropdown,
                province_dropdown,
                city_dropdown,
                district_dropdown,
                theme_dropdown,
                distance_slider,
                width_input,
                height_input,
                format_radio,
                no_crop_checkbox,
                lang_radio,
                layers_checkbox,
            ],
            outputs=[output_image, output_status],
        ).then(
            fn=on_generate_complete,
            inputs=[output_image, output_status],
            outputs=[output_image, output_status, download_btn],
        )

        # Footer
        gr.HTML("""
            <div style="text-align: center; margin-top: 24px; padding: 20px; color: #666; font-size: 13px; border-top: 1px solid #eee;">
                <p>项目地址: <a href="https://github.com/IsaacHuo/maptoposter" target="_blank" style="color: #764ba2; text-decoration: none; font-weight: bold;">GitHub - IsaacHuo/maptoposter</a></p>
                <p>✨ 欢迎提 <b>Issue</b> 和 <b>PR</b> | 鸣谢：该项目基于 <a href="https://github.com/originalankur/maptoposter" target="_blank" style="color: #666;">originalankur/maptoposter</a> 开发</p>
            </div>
        """)

    return demo


# --- Main Entry ---
if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        theme=gr.themes.Default(),
        css="""
        .header-title {
            text-align: center;
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 0.5em;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .header-subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 1.5em;
        }
        .section-title {
            font-weight: 600;
            font-size: 1.1em;
            margin-bottom: 0.5em;
            color: #333;
        }
        .output-image {
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        """,
    )
