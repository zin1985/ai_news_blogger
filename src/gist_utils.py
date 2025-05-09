import os
import requests

GIST_ID = os.environ.get("GIST_ID")
GIST_PAT = os.environ.get("GIST_PAT")

def load_posted_urls_from_gist():
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {"Authorization": f"Bearer {GIST_PAT}"}
    res = requests.get(url, headers=headers)
    urls = res.json()["files"]["posted_urls.json"]["content"].splitlines()
    return set(url.strip() for url in urls)

def save_posted_urls_to_gist(posted_urls):
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {"Authorization": f"Bearer {GIST_PAT}"}
    data = {
        "files": {
            "posted_urls.json": {
                "content": "\n".join(posted_urls)
            }
        }
    }
    requests.patch(url, headers=headers, json=data)
