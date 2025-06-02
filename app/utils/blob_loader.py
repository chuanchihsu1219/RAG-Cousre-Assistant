import os
from azure.storage.blob import BlobServiceClient
import zipfile


def download_and_extract_chroma_data(container_name, blob_name, download_dir, connection_string):
    os.makedirs(download_dir, exist_ok=True)
    local_zip_path = os.path.join(download_dir, "course_vector.zip")

    # 初始化 BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # 下載 ZIP 檔案
    with open(local_zip_path, "wb") as f:
        f.write(blob_client.download_blob().readall())

    # 解壓縮到資料夾
    with zipfile.ZipFile(local_zip_path, "r") as zip_ref:
        zip_ref.extractall(download_dir)

    # 刪除 zip
    os.remove(local_zip_path)
