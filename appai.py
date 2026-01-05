import streamlit as st
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI, Gemini

st.set_page_config(page_title="PandasAI Summary", layout="centered")
st.title("📊 PandasAI DataFrame Summary")

# ---- Choose LLM ----
llm_choice = st.selectbox(
    "Choose LLM",
    ["OpenAI", "Gemini (Google)"]
)

if llm_choice == "OpenAI":
    llm = OpenAI(api_token=st.secrets["OPENAI_API_KEY"])
else:
    llm = Gemini(api_key=st.secrets["GEMINI_API_KEY"])

# ---- Test DataFrame ----
df = pd.DataFrame({
    "Province": ["Bamyan", "Jawzjan", "Kabul", "Kapisa"],
    "Status": ["Ongoing", "Ongoing", "Ongoing", "Completed"]
})

st.subheader("Input Data")
st.dataframe(df)

# ---- PandasAI ----
sdf = SmartDataframe(df, config={"llm": llm})

if st.button("Summarize Data"):
    with st.spinner("Generating summary..."):
        summary = sdf.chat("Summarize this dataframe")
    st.success("Summary")
    st.write(summary)
