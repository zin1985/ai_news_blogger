import os
from openai import OpenAI

# OpenAIクライアントの初期化（APIキーは環境変数から取得）
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def summarize_article(text):
    # GPT-4を使って200字以内に要約
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "以下の文章を200字以内で簡潔に要約してください。"},
            {"role": "user", "content": text}
        ]
    )
    # 要約された文章を返す
    return response.choices[0].message.content.strip()
