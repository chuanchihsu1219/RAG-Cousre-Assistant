# setup_embedding_data.py
import os
import zipfile
import requests

AZURE_BLOB_URL = "https://<your_blob_storage_url>/chroma_data.zip"
# Todo: Replace <your_blob_storage_url> with your actual Azure Blob Storage URL

def download_and_extract():
    if os.path.exists("./persist/chroma_data"):
        print("Chroma embedding 已存在，不需下載")
        return

    os.makedirs("./persist", exist_ok=True)
    zip_path = "./persist/chroma_data.zip"
    print("下載 embedding 中...")
    with requests.get(AZURE_BLOB_URL, stream=True) as r:
        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    print("解壓縮中...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall("./persist")
    os.remove(zip_path)
    print("✅ 完成")


if __name__ == "__main__":
    download_and_extract()
