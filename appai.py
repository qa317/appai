import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

st.set_page_config(page_title="Gemini + DataFrame Q&A", layout="centered")

st.title("📊 Ask Questions About a DataFrame (Gemini)")

# ----------------------------
# Sample DataFrame (VERY SMALL)
# ----------------------------
df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie", "Diana"],
    "Age": [23, 30, 35, 28],
    "Department": ["HR", "Engineering", "Sales", "Engineering"],
    "Salary": [50000, 80000, 60000, 75000]
})

st.subheader("Sample Data")
st.dataframe(df, use_container_width=True)

# ----------------------------
# Gemini setup
# ----------------------------
api_key = st.secrets["GEMINI_API_KEY"]

if not api_key:
    st.warning("Please set GEMINI_API_KEY in Streamlit secrets or environment variables.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# ----------------------------
# Question input
# ----------------------------
st.subheader("Ask a question about the data")

question = st.text_input(
    "Example: Who earns the highest salary? or What is the average age?"
)

if st.button("Ask Gemini"):
    if not question.strip():
        st.error("Please enter a question.")
    else:
        # Convert DF to text for Gemini
        df_text = df.to_csv(index=False)

        prompt = f"""
You are a data analyst.
Answer the user's question using ONLY the data below.
If the answer cannot be found in the data, say "The data does not contain this information."

Data:
{df_text}

Question:
{question}
"""

        with st.spinner("Thinking..."):
            response = model.generate_content(prompt)

        st.subheader("Answer")
        st.write(response.text)
