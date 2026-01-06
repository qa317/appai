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
province_centroids = {
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

# Add lat/lon
counts["lat"] = counts["province"].map(lambda p: province_centroids.get(p, (None, None))[0])
counts["lon"] = counts["province"].map(lambda p: province_centroids.get(p, (None, None))[1])
counts = counts.dropna(subset=["lat", "lon"])

st.title("Province Bubble Map (Leaflet/Folium)")

use_cluster = st.toggle("Use clustering (better when zoomed out)", value=True)

# --- Create map ---
center_lat, center_lon = 34.5, 66.0  # Afghanistan-ish center
m = folium.Map(location=[center_lat, center_lon], zoom_start=6, tiles="CartoDB positron")

layer = MarkerCluster() if use_cluster else folium.FeatureGroup(name="Bubbles")
if use_cluster:
    m.add_child(layer)
else:
    m.add_child(layer)

def radius_from_count(c: int) -> int:
    # Smooth scaling that feels nice
    return int(10 + 10 * math.sqrt(c))

for _, row in counts.iterrows():
    prov = row["province"]
    c = int(row["count"])
    lat, lon = float(row["lat"]), float(row["lon"])

    r = radius_from_count(c)

    # Bubble with count label inside (DivIcon)
    html = f"""
    <div style="
        width:{r*2}px; height:{r*2}px;
        border-radius:50%;
        background: rgba(255, 140, 0, 0.35);
        border: 2px solid rgba(255, 140, 0, 0.85);
        display:flex; align-items:center; justify-content:center;
        font-weight:700; font-size:{max(12, r//2)}px;
        color: rgba(60, 35, 0, 0.95);
        ">
        {c}
    </div>
    """

    folium.Marker(
        location=[lat, lon],
        icon=folium.DivIcon(html=html),
        tooltip=f"{prov}: {c}",
    ).add_to(layer)

# Render in Streamlit
st_folium(m, width=None, height=650)
