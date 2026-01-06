import streamlit as st
import pandas as pd
import plotly.express as px

# --- Your data ---
df = pd.DataFrame({
    "province": [
        "Badakhshan", "Badghis", "Balkh", "Daykundi",
        "Kandahar", "Kapisa", "Laghman", "Logar", "Logar"
    ],
    "aa": ["a"] * 9
})

# --- Province centroids (approx; tweak if you want) ---
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

# Map lat/lon
counts["lat"] = counts["province"].map(lambda p: province_centroids.get(p, (None, None))[0])
counts["lon"] = counts["province"].map(lambda p: province_centroids.get(p, (None, None))[1])
counts = counts.dropna(subset=["lat", "lon"])

st.title("Province Counts Map")

# --- Controls ---
zoom = st.slider("Zoom", min_value=4.0, max_value=9.0, value=5.5, step=0.5)
show_labels = st.toggle("Show count labels", value=True)

# Simple rule: only show text if zoom is high enough (and toggle is on)
enable_text = show_labels and zoom >= 6.5

# --- Fancy map ---
fig = px.scatter_mapbox(
    counts,
    lat="lat",
    lon="lon",
    size="count",
    color="count",
    hover_name="province",
    hover_data={"count": True, "lat": False, "lon": False},
    zoom=zoom,
    height=650,
    mapbox_style="open-street-map",  # no token needed
)

# Add text labels
if enable_text:
    fig.update_traces(
        text=counts["count"].astype(str),
        textposition="top center",
        mode="markers+text"
    )
else:
    fig.update_traces(mode="markers")

# Make it prettier
fig.update_layout(
    margin=dict(l=0, r=0, t=40, b=0),
    title=dict(text="Counts by Province", x=0.02),
)

# Bubble sizing nicer
fig.update_traces(marker=dict(sizemode="area", sizemin=8))

st.plotly_chart(fig, use_container_width=True)
