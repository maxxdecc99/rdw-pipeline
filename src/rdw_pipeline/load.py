from pathlib import Path

from google.cloud import storage

PROJECT = "rdw-pipeline-0000"
BUCKET = "rdw-pipeline-0000-data"

def upload(local_path):
    client = storage.Client(project=PROJECT)
    bucket = client.bucket(BUCKET)

    blob_name = f"processed/{Path(local_path).name}"

    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_path)

    return f"gs://{BUCKET}/{blob_name}"
