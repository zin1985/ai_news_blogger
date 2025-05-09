import os
import requests

GIST_ID = os.environ.get("GIST_ID")
GIST_PAT = os.environ.get("GIST_PAT")

def load_posted_urls_from_gist():
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {"Authorization": f"Bearer {GIST_PAT}"}
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        print(f"❌ Gist取得失敗: {res.status_code}")
        print("レスポンス:", res.text)
        return set()

    data = res.json()

    files = data.get("files", {})
    print("📄 Gist内のファイル一覧:", list(files.keys()))

    if "posted_urls.json" not in files:
        print("⚠️ 'posted_urls.json' が Gist に見つかりません。初期化します。")
        return set()

    content = files["posted_urls.json"].get("content", "")
    return set(line.strip() for line in content.splitlines() if line.strip())

def save_posted_urls_to_gist(posted_urls):
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {"Authorization": f"Bearer {GIST_PAT}"}
    content = "\n".join(posted_urls)
    data = {
        "files": {
            "posted_urls.json": {
                "content": content
            }
        }
    }
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code == 200:
        print("✅ Gist更新成功")
    else:
        print(f"❌ Gist更新失敗: {response.status_code}")
        print("レスポンス:", response.text)
