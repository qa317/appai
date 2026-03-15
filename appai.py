import streamlit as st

st.set_page_config(page_title="Edito A1 Audio Player", page_icon="🎧")

st.title("🎧 Edito A1 Audio Player")

audio_number = st.number_input(
    "Choose audio number",
    min_value=1,
    max_value=200,
    value=1,
    step=1
)

# folder number
folder_number = 40991 + audio_number

# format number with two digits
audio_str = f"{audio_number:02d}"

# # build URL
audio_url = f"https://e-didier.fr/datas/{folder_number}/{audio_str}_Edito_A1_Livre.mp3"

# st.write("Audio URL:")
# st.code(audio_url)

st.audio(audio_url)

st.link_button("Open audio in browser", audio_url)

# import streamlit as st
# import pandas as pd
# from google import genai

# st.set_page_config(page_title="Gemini + DF Q&A", layout="centered")
# st.title("📊 Gemini Q&A on a tiny DataFrame")

# # 1) Tiny sample DataFrame
# df = pd.DataFrame(
#     {
#         "Name": ["Alice", "Bob", "Charlie", "Diana"],
#         "Age": [23, 30, 35, 28],
#         "Department": ["HR", "Engineering", "Sales", "Engineering"],
#         "Salary": [50000, 80000, 60000, 75000],
#     }
# )



# st.subheader("Data")
# st.dataframe(df, use_container_width=True)

# # 2) Read API key from Streamlit secrets
# if "GEMINI_API_KEY" not in st.secrets:
#     st.error('Missing secret: GEMINI_API_KEY (add it in Streamlit "Secrets")')
#     st.stop()

# client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# # 3) Ask a question
# st.subheader("Ask a question about the data")
# q = st.text_input("Example: Who has the highest salary?")

# if st.button("Ask Gemini"):
#     if not q.strip():
#         st.warning("Type a question first.")
#         st.stop()

#     df_text = df.to_csv(index=False)

#     prompt = f"""
# You are a data analyst.
# Answer using ONLY the data provided below.
# If the answer is not in the data, say: "The data does not contain this information."

# DATA (CSV):
# {df_text}

# QUESTION:
# {q}
# """.strip()

#     with st.spinner("Thinking..."):
#         resp = client.models.generate_content(
#             model="gemini-2.5-flash",
#             contents=prompt,
#         )

#     st.subheader("Answer")
#     st.write(resp.text)
