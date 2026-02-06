import streamlit as st
import pandas as pd
from pandas_ai import PandasAI
from pandas_ai.llms.openai import OpenAI

# ——— Set up the LLM ———
llm = OpenAI()

# ——— App Title ———
st.title("📊 Pandas AI + Streamlit Explorer")

st.markdown("""
Upload a CSV file, explore the data, and ask questions in natural language!
""")

# ——— File Upload ———
uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.write("### 📋 Data Preview")
    st.dataframe(df)

    st.write("### Ask a question about the data")

    user_question = st.text_input("Type your question here:")

    if user_question:
        with st.spinner("Analyzing with Pandas AI..."):
            pandas_ai = PandasAI(llm)
            try:
                answer = pandas_ai.run(df, prompt=user_question)
                st.write("### 🧠 Answer:")
                st.write(answer)
            except Exception as e:
                st.error(f"Oops, something went wrong: {e}")

else:
    st.write("Upload a CSV file to begin!")
