import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import math

# --- Your data ---
df = pd.DataFrame({
    "province": [
        "Badakhshan", "Badghis", "Balkh", "Daykundi",
        "Kandahar", "Kapisa", "Laghman", "Logar", "Logar"
    ],
    "aa": ["a"] * 9
})

# --- Province centroids (approx) ---
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

# --- Count occurrences ---
counts = df.groupby("province").size().reset_index(name="count")
counts["lat"] = counts["province"].map(lambda p: centroids[p][0])
counts["lon"] = counts["province"].map(lambda p: centroids[p][1])

# --- Map (nice tiles) ---
m = folium.Map(location=[34.5, 66.0], zoom_start=6, tiles="CartoDB positron")

# --- Cluster layer ---
cluster = MarkerCluster(disableClusteringAtZoom=8)  # stops clustering when zoomed in enough
m.add_child(cluster)

def bubble_size(c: int) -> int:
    # bubble diameter in pixels (nice scaling)
    return int(26 + 10 * math.sqrt(c))

for _, r in counts.iterrows():
    prov, c, lat, lon = r["province"], int(r["count"]), r["lat"], r["lon"]
    d = bubble_size(c)
    font = max(12, d // 3)

    html = f"""
    <div style="
        width:{d}px; height:{d}px;
        border-radius:50%;
        background: rgba(255,140,0,0.35);
        border: 2px solid rgba(255,140,0,0.9);
        display:flex; align-items:center; justify-content:center;
        font-weight:700; font-size:{font}px;
        color: rgba(60,35,0,0.95);
        ">
        {c}
    </div>
    """

    folium.Marker(
        location=[lat, lon],
        icon=folium.DivIcon(html=html),
        tooltip=f"{prov}: {c}",
    ).add_to(cluster)

st_folium(m, height=580, use_container_width=True)
