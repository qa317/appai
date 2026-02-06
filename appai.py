import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Hugging Face + DF Q&A", layout="centered")
st.title("📊 Ask Questions About a DataFrame (Hugging Face API)")

# Sample DataFrame
df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie", "Diana"],
    "Age": [23, 30, 35, 28],
    "Department": ["HR", "Engineering", "Sales", "Engineering"],
    "Salary": [50000, 80000, 60000, 75000],
})

st.subheader("Sample Data")
st.dataframe(df, use_container_width=True)

# API key from secrets
if "HF_API_TOKEN" not in st.secrets:
    st.error('Add HF_API_TOKEN in Streamlit secrets.')
    st.stop()

HF_API_TOKEN = st.secrets["HF_API_TOKEN"]

st.subheader("Ask a question about the data")
question = st.text_input("Example: Who has the highest salary?")

# Choose model (many free models work)
model = st.selectbox(
    "Model",
    ["tiiuae/falcon-7b-instruct", "google/flan-t5-xl", "databricks/dolly-v2-12b"],
    index=0
)

def call_hf_inference(prompt: str, model_name: str) -> str:
    url = f"https://api-inference.huggingface.co/models/{model_name}"
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"inputs": prompt, "options": {"wait_for_model": True}}

    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()

    # The structure differs by model — many return text directly
    if isinstance(data, dict) and "error" in data:
        return f"Error: {data['error']}"

    # Some outputs are lists
    if isinstance(data, list) and len(data) > 0:
        # For most HF GOV models
        return data[0].get("generated_text", str(data[0]))

    return str(data)

if st.button("Ask HF"):
    if not question.strip():
        st.warning("Type a question first.")
    else:
        df_text = df.to_csv(index=False)
        prompt = (
            "You are a data analyst. Answer using ONLY the data below. "
            'If you cannot find the answer, respond: "The data does not contain this information."\n\n'
            f"Data (CSV):\n{df_text}\n\nQUESTION:\n{question}"
        )
        with st.spinner("Thinking..."):
            try:
                answer = call_hf_inference(prompt, model)
                st.subheader("Answer")
                st.write(answer)
            except Exception as e:
                st.error(f"Hugging Face API error: {e}")
