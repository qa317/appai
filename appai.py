import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="DeepSeek + DF Q&A", layout="centered")
st.title("📊 Ask Questions About a DataFrame (DeepSeek)")

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

# 2) Read API key from Streamlit secrets
# In Streamlit Cloud -> Settings -> Secrets:
# DEEPSEEK_API_KEY = "..."
if "DEEPSEEK_API_KEY" not in st.secrets:
    st.error('Missing secret: DEEPSEEK_API_KEY (add it in Streamlit "Secrets").')
    st.stop()

DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]

# 3) UI input
st.subheader("Ask a question about the data")
question = st.text_input("Example: Who has the highest salary?")

# Optional: choose model (simple)
model = st.selectbox(
    "Model",
    ["deepseek-chat", "deepseek-reasoner"],
    index=0,
    help="deepseek-chat is general chat; deepseek-reasoner is reasoning-focused."
)

def ask_deepseek(df: pd.DataFrame, q: str, model_name: str) -> str:
    df_text = df.to_csv(index=False)

    system_msg = (
        "You are a data analyst. Answer the user's question using ONLY the data provided. "
        'If the answer cannot be found in the data, say: "The data does not contain this information."'
    )

    user_msg = f"DATA (CSV):\n{df_text}\n\nQUESTION:\n{q}"

    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        "temperature": 0.2,
    }

    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()

    # DeepSeek returns OpenAI-style choices/message
    return data["choices"][0]["message"]["content"]

if st.button("Ask DeepSeek"):
    if not question.strip():
        st.warning("Type a question first.")
    else:
        try:
            with st.spinner("Thinking..."):
                answer = ask_deepseek(df, question, model)
            st.subheader("Answer")
            st.write(answer)
        except requests.HTTPError as e:
            st.error(f"DeepSeek API error: {e}\n\nResponse: {e.response.text if e.response is not None else ''}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")
