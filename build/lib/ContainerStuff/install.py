import requests
import os

user = "kauanmezavila"
repo = "harbor"
file = "HarborSpecs"

def download_harb():
    api_url = f"https://api.github.com/repos/{user}/{repo}/contents/{file}"

    response = requests.get(api_url)
    response.raise_for_status()

    data = response.json()

    download_url = data["download_url"]

    downloaded_file = requests.get(download_url)
    downloaded_file.raise_for_status()

    with open("", "wb") as f:
        f.write(downloaded_file.content)

    print("Arquivo baixado com sucesso!")