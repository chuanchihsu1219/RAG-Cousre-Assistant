# app/utils/blob_loader.py
import os
from azure.storage.blob import BlobServiceClient


def download_chroma_from_blob(connection_string, container_name, blob_prefix="", local_dir):
    os.makedirs(local_dir, exist_ok=True)
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    blobs = container_client.list_blobs(name_starts_with=blob_prefix)
    for blob in blobs:
        blob_name = blob.name
        relative_path = blob_name.replace(blob_prefix, "", 1).lstrip("/")
        local_path = os.path.join(local_dir, relative_path)

        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as file:
            blob_data = container_client.download_blob(blob_name)
            file.write(blob_data.readall())
