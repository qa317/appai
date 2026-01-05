import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI

# Create the DataFrame
df = pd.DataFrame({
    "Province": ["Bamyan", "Jawzjan", "Kabul", "Kapisa"],
    "Status": ["Ongoing", "Ongoing", "Ongoing", "Completed"]
})

# Configure LLM (example: OpenAI)
llm = OpenAI(api_token="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")

# Wrap DataFrame with PandasAI
sdf = SmartDataframe(df, config={"llm": llm})

# Ask PandasAI to summarize
summary = sdf.chat("Summarize this dataframe")

print(summary)
