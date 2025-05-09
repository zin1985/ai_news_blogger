import os
import openai

def summarize_article(text):
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "以下の文章を200字以内で簡潔に要約してください。"},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message['content'].strip()
