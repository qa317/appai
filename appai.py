import pandas as pd
import plotly.express as px
import streamlit as st

# Province centroids (approx)
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
df = pd.DataFrame({
    "province": [
        "Badakhshan", "Badghis", "Balkh", "Daykundi",
        "Kandahar", "Kapisa", "Laghman", "Logar", "Logar"
    ],
    "aa": ["a"] * 9
})
df_counts = (
    df.groupby("province")
      .size()
      .reset_index(name="count")
)

df_counts["lat"] = df_counts["province"].map(lambda x: province_centroids[x][0])
df_counts["lon"] = df_counts["province"].map(lambda x: province_centroids[x][1])

fig = px.scatter_mapbox(
    df_counts,
    lat="lat",
    lon="lon",
    size="count",
    color="count",
    zoom=5,
    mapbox_style="open-street-map",
)

st.plotly_chart(fig, use_container_width=True)
