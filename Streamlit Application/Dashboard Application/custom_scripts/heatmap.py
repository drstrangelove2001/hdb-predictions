from branca.colormap import LinearColormap
import numpy as np
import folium

METRIC_MAP = {
    'monthly_rent': 'Average Monthly Rent (SGD)',
    'resale_price': 'Average Resale Price (SGD)',
    'count': 'Number of transactions'
}

def heatmap(map_data, metric):
    min_metric = map_data[metric].min()
    max_metric = map_data[metric].max()
    # Normalize 0-1 scale
    def normalize_price(price): 
        return 0 if np.isnan(price) else (price - min_metric) / (max_metric - min_metric)
    
    map_data['normalized_metric'] = map_data[metric].apply(normalize_price)

    colormap = LinearColormap(
        vmin=min_metric,
        vmax=max_metric,
        colors=['#FFFFE0', '#FFFF00', '#FFA500', '#FF4500'],  # Shades
        caption=f'Normalized {METRIC_MAP[metric]}'
    )

    tooltip = folium.GeoJsonTooltip(
        fields=['PLN_AREA_N', metric],
        aliases=['Town:', f'{METRIC_MAP[metric]}'],
        localize=True,
        sticky=False,
        labels=True,
        style="""
            background-color: #F0EFEF;
            border: 2px solid black;
            border-radius: 3px;
            box-shadow: 3px;
        """,
        max_width=800,
    )

    popup = folium.GeoJsonPopup(
        fields=['PLN_AREA_N', metric],
        aliases=['Town', METRIC_MAP[metric]],
        localize=True,
        labels=True,
        style="background-color: yellow;",
    )

    m = folium.Map(location=[1.3521, 103.8198], zoom_start=11, tiles="CartoDB positron") # centered in Singapore

    g = folium.GeoJson(
        map_data,
        style_function=lambda x: {
            "fillColor": colormap(x['properties'][metric]) if x['properties'][metric] is not None else "lightgray",
            "color": "black",
            "fillOpacity": x['properties']['normalized_metric'] if x['properties'][metric] is not None else 1,
            'weight': 1
        },
        tooltip=tooltip,
        popup=popup,
    ).add_to(m)

    colormap.add_to(m)

    return m