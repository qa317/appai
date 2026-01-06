import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import math

# --- Data ---
df = pd.DataFrame({
    "province": [
        "Badakhshan", "Badghis", "Balkh", "Daykundi",
        "Kandahar", "Kapisa", "Laghman", "Logar", "Logar"
    ]
})

# --- Province centroids ---
centroids = {
    "Badakhshan": (36.7, 70.8),
    "Badghis": (35.2, 63.8),
    "Balkh": (36.7, 67.1),
    "Daykundi": (33.7, 66.0),
    "Kandahar": (31.6, 65.7),
    "Kapisa": (34.9, 69.6),
    "Laghman": (34.7, 70.2),
    "Logar": (34.0, 69.2),
}

counts = df.groupby("province").size().reset_index(name="count")
counts["lat"] = counts["province"].map(lambda p: centroids[p][0])
counts["lon"] = counts["province"].map(lambda p: centroids[p][1])

# --- Map ---
m = folium.Map(location=[34.5, 66.0], zoom_start=6, tiles="CartoDB positron")

# --- Beautiful cluster style ---
cluster = MarkerCluster(
    disableClusteringAtZoom=8,
    icon_create_function="""
    function(cluster) {
        var count = cluster.getChildCount();
        var size = Math.max(30, Math.min(60, 20 + Math.sqrt(count)*12));
        return new L.DivIcon({
            html: `<div style="
                width:${size}px;height:${size}px;
                border-radius:50%;
                background:rgba(255,140,0,0.35);
                border:2px solid rgba(255,140,0,0.9);
                display:flex;
                align-items:center;
                justify-content:center;
                font-weight:700;
                color:#3c2300;
                font-size:${size/3}px;
            ">${count}</div>`
        });
    }
    """
)

m.add_child(cluster)

def bubble_diameter(c):
    return int(26 + 10 * math.sqrt(c))

# --- Markers ---
for _, r in counts.iterrows():
    d = bubble_diameter(r["count"])
    font = max(12, d // 3)

    html = f"""
    <div style="
        width:{d}px;height:{d}px;
        border-radius:50%;
        background:rgba(255,140,0,0.35);
        border:2px solid rgba(255,140,0,0.9);
        display:flex;
        align-items:center;
        justify-content:center;
        font-weight:700;
        font-size:{font}px;
        color:#3c2300;
    ">{r['count']}</div>
    """

    folium.Marker(
        location=[r["lat"], r["lon"]],
        icon=folium.DivIcon(html=html),
        tooltip=f"{r['province']}: {r['count']}"
    ).add_to(cluster)

st_folium(m, height=650, use_container_width=True)
