import os
from azure.storage.blob import BlobServiceClient
import zipfile


def download_and_extract_chroma_data(container_name, blob_name, download_dir, connection_string):
    try:
        print("🔽 開始下載 blob 並解壓縮...")

        os.makedirs(download_dir, exist_ok=True)
        local_zip_path = os.path.join(download_dir, "course_vector.zip")

        # 初始化 BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        # 下載 ZIP 檔案
        with open(local_zip_path, "wb") as f:
            f.write(blob_client.download_blob().readall())
        print("✅ ZIP 下載成功！")

        # 解壓縮
        with zipfile.ZipFile(local_zip_path, "r") as zip_ref:
            zip_ref.extractall(download_dir)
        print("✅ 解壓完成！")

        # 刪除 zip
        os.remove(local_zip_path)
        print("🗑️ zip 刪除完成")

        # 檢查資料夾內容
        print("📂 解壓後檔案檢查：")
        for root, dirs, files in os.walk(download_dir):
            print(f"📁 {root}")
            for f in files:
                fp = os.path.join(root, f)
                size = os.path.getsize(fp)
                print(f"   - {f} ({size / 1024:.1f} KB)")

    except Exception as e:
        print("❌ 下載或解壓失敗：", e)
