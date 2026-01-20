# -*- coding: utf-8 -*-
"""
Gradio Web Interface for City Map Poster Generator
"""

import os
import json
import gradio as gr
import tempfile
from datetime import datetime

# Import from the main module
from cities_data import (
    CITIES, 
    get_countries, 
    get_provinces, 
    get_cities, 
    search_cities,
    get_city_full_name
)

# --- Constants ---
THEMES_DIR = "themes"
FONTS_DIR = "fonts"
POSTERS_DIR = "posters"


def get_available_themes():
    """Scans the themes directory and returns a list of available theme names."""
    if not os.path.exists(THEMES_DIR):
        return []
    
    themes = []
    for file in sorted(os.listdir(THEMES_DIR)):
        if file.endswith('.json'):
            theme_name = file[:-5]
            themes.append(theme_name)
    return themes


def load_theme_info(theme_name):
    """Load theme details for preview."""
    theme_file = os.path.join(THEMES_DIR, f"{theme_name}.json")
    if os.path.exists(theme_file):
        with open(theme_file, 'r') as f:
            return json.load(f)
    return None


def get_theme_preview_html(theme_name):
    """Generate HTML preview for a theme."""
    theme = load_theme_info(theme_name)
    if not theme:
        return "<p>主题加载失败</p>"
    
    # Create color swatches
    colors = [
        ("背景", theme.get("bg", "#FFFFFF")),
        ("文字", theme.get("text", "#000000")),
        ("高速公路", theme.get("road_motorway", "#000000")),
        ("主干道", theme.get("road_primary", "#333333")),
        ("次干道", theme.get("road_secondary", "#666666")),
        ("水域", theme.get("water", "#C0C0C0")),
        ("公园", theme.get("parks", "#F0F0F0")),
    ]
    
    html = f"""
    <div style="padding: 12px; background: {theme.get('bg', '#FFFFFF')}; border-radius: 8px; border: 1px solid #ddd;">
        <h4 style="color: {theme.get('text', '#000000')}; margin: 0 0 8px 0; font-size: 14px;">
            {theme.get('name', theme_name)}
        </h4>
        <p style="color: {theme.get('text', '#000000')}; opacity: 0.7; margin: 0 0 12px 0; font-size: 12px;">
            {theme.get('description', '')}
        </p>
        <div style="display: flex; flex-wrap: wrap; gap: 6px;">
    """
    
    for label, color in colors:
        text_color = "#fff" if sum(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) < 384 else "#000"
        html += f"""
            <div style="display: flex; align-items: center; gap: 4px;">
                <div style="width: 20px; height: 20px; background: {color}; border-radius: 4px; border: 1px solid #ccc;"></div>
                <span style="font-size: 10px; color: {theme.get('text', '#000')}; opacity: 0.8;">{label}</span>
            </div>
        """
    
    html += "</div></div>"
    return html


def generate_poster(
    city_input, 
    country, 
    province, 
    city_dropdown,
    theme_name, 
    distance, 
    width, 
    height, 
    output_format,
    no_crop,
    progress=gr.Progress()
):
    """
    Generate the map poster with given parameters.
    """
    # Import here to avoid circular imports and ensure THEME is set correctly
    import create_map_poster as cmp
    
    # Determine which city to use
    if city_input and city_input.strip():
        # User typed in a city - parse it
        parts = [p.strip() for p in city_input.split(',')]
        if len(parts) >= 2:
            selected_city = parts[0]
            selected_country = parts[-1] if len(parts) >= 2 else country
        else:
            selected_city = city_input.strip()
            selected_country = country if country else "China"
    else:
        # Use dropdown selection
        selected_city = city_dropdown
        selected_country = country
    
    if not selected_city:
        return None, "❌ 请选择或输入城市名称"
    
    if not selected_country:
        return None, "❌ 请选择国家"
    
    progress(0.1, desc="正在加载主题...")
    
    # Load theme
    cmp.THEME = cmp.load_theme(theme_name)
    
    progress(0.2, desc="正在获取坐标...")
    
    try:
        coords = cmp.get_coordinates(selected_city, selected_country)
    except Exception as e:
        return None, f"❌ 无法找到城市坐标: {str(e)}"
    
    progress(0.3, desc="正在生成海报...")
    
    # Generate output filename
    output_file = cmp.generate_output_filename(selected_city, theme_name, output_format)
    
    try:
        cmp.create_poster(
            selected_city, 
            selected_country, 
            coords, 
            distance, 
            output_file, 
            output_format,
            width=width, 
            height=height, 
            no_crop=no_crop
        )
        
        progress(1.0, desc="完成!")
        
        return output_file, f"✅ 海报生成成功！保存至: {output_file}"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, f"❌ 生成失败: {str(e)}"


def update_provinces(country):
    """Update province dropdown based on country selection."""
    provinces = get_provinces(country)
    if provinces:
        return gr.update(choices=provinces, value=provinces[0], visible=True)
    return gr.update(choices=[], value=None, visible=False)


def update_cities(country, province):
    """Update city dropdown based on province selection."""
    cities = get_cities(country, province)
    if cities:
        return gr.update(choices=cities, value=cities[0])
    return gr.update(choices=[], value=None)


def on_city_search(query):
    """Handle city search and return formatted results."""
    results = search_cities(query)
    if results:
        # Format as "City, Province, Country" for display
        formatted = [get_city_full_name(c, p, co) for c, p, co in results]
        return gr.update(choices=formatted, visible=True)
    return gr.update(choices=[], visible=False)


def on_theme_change(theme_name):
    """Update theme preview when theme changes."""
    return get_theme_preview_html(theme_name)


# --- Build Gradio Interface ---
def create_interface():
    """Create and return the Gradio interface."""
    
    # Get initial data
    countries = get_countries()
    themes = get_available_themes()
    default_country = "中国"
    default_provinces = get_provinces(default_country)
    default_province = default_provinces[0] if default_provinces else None
    default_cities = get_cities(default_country, default_province) if default_province else []
    default_city = default_cities[0] if default_cities else None
    default_theme = themes[0] if themes else "feature_based"
    
    with gr.Blocks(
        title="城市地图海报生成器",
    ) as demo:
        
        # Header
        gr.HTML("""
            <div class="header-title">🗺️ 城市地图海报生成器</div>
            <div class="header-subtitle">选择任意城市，自定义主题风格，生成精美地图海报</div>
        """)
        
        with gr.Row():
            # Left Column - Controls
            with gr.Column(scale=1):
                
                # City Selection Section
                gr.HTML('<div class="section-title">📍 城市选择</div>')
                
                with gr.Tab("🔍 搜索"):
                    city_search = gr.Textbox(
                        label="搜索城市",
                        placeholder="输入城市名称，如: Tokyo, Paris, 广州...",
                        info="输入城市名称进行搜索，支持中英文"
                    )
                
                with gr.Tab("📋 级联选择"):
                    country_dropdown = gr.Dropdown(
                        choices=countries,
                        value=default_country,
                        label="选择国家",
                        interactive=True
                    )
                    
                    province_dropdown = gr.Dropdown(
                        choices=default_provinces,
                        value=default_province,
                        label="选择省份/州",
                        interactive=True
                    )
                    
                    city_dropdown = gr.Dropdown(
                        choices=default_cities,
                        value=default_city,
                        label="选择城市",
                        interactive=True
                    )
                
                gr.HTML("<hr style='margin: 20px 0; border-color: #eee;'>")
                
                # Theme Section
                gr.HTML('<div class="section-title">🎨 主题风格</div>')
                
                theme_dropdown = gr.Dropdown(
                    choices=themes,
                    value=default_theme,
                    label="选择主题",
                    interactive=True
                )
                
                theme_preview = gr.HTML(
                    value=get_theme_preview_html(default_theme),
                    label="主题预览"
                )
                
                gr.HTML("<hr style='margin: 20px 0; border-color: #eee;'>")
                
                # Parameters Section
                gr.HTML('<div class="section-title">⚙️ 参数设置</div>')
                
                distance_slider = gr.Slider(
                    minimum=4000,
                    maximum=30000,
                    value=12000,
                    step=1000,
                    label="地图范围 (米)",
                    info="4000-6000: 小城区 | 8000-12000: 中等城市 | 15000+: 大都市"
                )
                
                with gr.Row():
                    width_input = gr.Number(
                        value=12.0,
                        label="宽度 (英寸)",
                        minimum=6,
                        maximum=24
                    )
                    height_input = gr.Number(
                        value=16.0,
                        label="高度 (英寸)",
                        minimum=8,
                        maximum=32
                    )
                
                format_radio = gr.Radio(
                    choices=["png", "svg", "pdf"],
                    value="png",
                    label="输出格式",
                    info="PNG: 适合打印 | SVG: 矢量图 | PDF: 文档"
                )
                
                no_crop_checkbox = gr.Checkbox(
                    value=False,
                    label="保留边距 (不裁剪)",
                    info="勾选后保留海报边缘背景"
                )
                
                # Generate Button
                generate_btn = gr.Button(
                    "🚀 生成海报",
                    variant="primary",
                    size="lg"
                )
            
            # Right Column - Output
            with gr.Column(scale=1):
                gr.HTML('<div class="section-title">🖼️ 生成结果</div>')
                
                output_image = gr.Image(
                    label="海报预览",
                    type="filepath",
                    elem_classes=["output-image"],
                    height=600,
                    interactive=False
                )
                
                output_status = gr.Textbox(
                    label="状态",
                    interactive=False
                )
                
                download_btn = gr.DownloadButton(
                    label="📥 下载海报",
                    visible=False
                )
        
        # --- Event Handlers ---
        
        # Country change -> update provinces
        country_dropdown.change(
            fn=update_provinces,
            inputs=[country_dropdown],
            outputs=[province_dropdown]
        )
        
        # Province change -> update cities
        province_dropdown.change(
            fn=update_cities,
            inputs=[country_dropdown, province_dropdown],
            outputs=[city_dropdown]
        )
        
        # Theme change -> update preview
        theme_dropdown.change(
            fn=on_theme_change,
            inputs=[theme_dropdown],
            outputs=[theme_preview]
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
                city_search,
                country_dropdown,
                province_dropdown,
                city_dropdown,
                theme_dropdown,
                distance_slider,
                width_input,
                height_input,
                format_radio,
                no_crop_checkbox
            ],
            outputs=[output_image, output_status]
        ).then(
            fn=on_generate_complete,
            inputs=[output_image, output_status],
            outputs=[output_image, output_status, download_btn]
        )
        
        # Footer
        gr.HTML("""
            <div style="text-align: center; margin-top: 24px; padding: 12px; color: #888; font-size: 12px;">
                <p>数据来源: © OpenStreetMap contributors | 地理编码: Nominatim</p>
                <p>提示: 生成大范围地图可能需要较长时间，请耐心等待</p>
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
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="slate",
        ),
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
        """
    )
