import streamlit as st
import pandas as pd
import folium
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

# --- Pretty base map ---
m = folium.Map(location=[34.5, 66.0], zoom_start=6, tiles="CartoDB positron")

# Smooth, nice sizing
def bubble_radius(c):
    return 6 + 6 * math.sqrt(c)

for _, r in counts.iterrows():
    prov, c, lat, lon = r["province"], int(r["count"]), r["lat"], r["lon"]

    folium.CircleMarker(
        location=[lat, lon],
        radius=bubble_radius(c),
        weight=2,
        color="#ff8c00",
        fill=True,
        fill_color="#ff8c00",
        fill_opacity=0.35,
        tooltip=f"{prov}: {c}",
    ).add_to(m)

st_folium(m, height=650, use_container_width=True)
