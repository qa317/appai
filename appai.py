import streamlit as st
import pandas as pd
from openai import OpenAI

st.set_page_config(page_title="Kimi + DF Q&A", layout="centered")
st.title("📊 Ask Questions About a DataFrame (Kimi / Moonshot)")

# 1) Tiny sample DataFrame
df = pd.DataFrame(
    {
        "Name": ["Alice", "Bob", "Charlie", "Diana"],
        "Age": [23, 30, 35, 28],
        "Department": ["HR", "Engineering", "Sales", "Engineering"],
        "Salary": [50000, 80000, 60000, 75000],
    }
)

st.subheader("Sample Data")
st.dataframe(df, use_container_width=True)

# 2) Secrets: API key + optional base URL + optional model
# Streamlit Cloud -> Settings -> Secrets:
# MOONSHOT_API_KEY = "sk-..."
# (optional) MOONSHOT_BASE_URL = "https://api.moonshot.cn/v1"  or "https://api.moonshot.ai/v1"
# (optional) MOONSHOT_MODEL = "kimi-k2-0711-preview"
if "MOONSHOT_API_KEY" not in st.secrets:
    st.error('Missing secret: MOONSHOT_API_KEY (add it in Streamlit "Secrets").')
    st.stop()

base_url = st.secrets.get("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1")
default_model = st.secrets.get("MOONSHOT_MODEL", "kimi-k2-0711-preview")

client = OpenAI(api_key=st.secrets["MOONSHOT_API_KEY"], base_url=base_url)

# 3) Simple UI
st.subheader("Ask a question about the data")
question = st.text_input("Example: Who has the highest salary?")

# Let you override model from UI (in case your account has different model IDs)
model = st.text_input("Model name", value=default_model)

def ask_kimi(q: str) -> str:
    df_text = df.to_csv(index=False)

    system_msg = (
        "You are a data analyst. Answer the user's question using ONLY the data provided. "
        'If the answer cannot be found in the data, say: "The data does not contain this information."'
    )

    user_msg = f"DATA (CSV):\n{df_text}\n\nQUESTION:\n{q}"

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content

if st.button("Ask Kimi"):
    if not question.strip():
        st.warning("Type a question first.")
    else:
        try:
            with st.spinner("Thinking..."):
                answer = ask_kimi(question)
            st.subheader("Answer")
            st.write(answer)
        except Exception as e:
            st.error(
                "Kimi API call failed.\n\n"
                f"Base URL: {base_url}\n"
                f"Model: {model}\n\n"
                f"Error: {e}"
            )
            st.info(
                "Tip: If it says 'model not found', change the model name to one enabled in your Moonshot console."
            )
