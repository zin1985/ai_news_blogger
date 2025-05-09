
import os
import requests
import json

GIST_ID = os.environ.get("GIST_ID")
GIST_PAT = os.environ.get("GIST_PAT")

def load_posted_urls_from_gist():
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {"Authorization": f"Bearer {GIST_PAT}"}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print("❌ Gist取得失敗:", res.status_code)
        return set()
    data = res.json()
    content = data.get("files", {}).get("posted_urls.json", {}).get("content", "")
    return set(line.strip() for line in content.splitlines() if line.strip())

def save_posted_urls_to_gist(posted_urls):
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {"Authorization": f"Bearer {GIST_PAT}"}
    json_content = json.dumps({"urls": list(posted_urls)}, indent=2, ensure_ascii=False)
    data = {
        "files": {
            "posted_urls.json": {
                "content": json_content
            }
        }
    }
    requests.patch(url, headers=headers, json=data)
