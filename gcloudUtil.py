from google.cloud import storage
import datetime
from credentialUtils import get_credentials

def list_blobs(bucket_name):
    """Lists all the blobs in the bucket."""

    storage_client = storage.Client(credentials=get_credentials())

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name)

    # Note: The call returns a response only when the iterator is consumed.
    for blob in blobs:
        print(blob.name)

# print(list_blobs("earthquake_bukt"))

def generate_download_signed_url_v4(bucket_name, blob_name):
    """Generates a v4 signed URL for downloading a blob.

    Note that this method requires a service account key file. You can not use
    this if you are using Application Default Credentials from Google Compute
    Engine or from the Google Cloud SDK.
    """
    # bucket_name = 'your-bucket-name'
    # blob_name = 'your-object-name'

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    print(blob)
    url = blob.generate_signed_url(
        version="v4",
        # This URL is valid for 15 minutes
        expiration=datetime.timedelta(minutes=15),
        # Allow GET requests using this URL.
        method="GET",
        credentials=get_credentials()
    )

    print("Generated GET signed URL:")
    print(url)
    return url

def generate_object_urls(bucket_name="earthquake_bukt"):

    result = []

    storage_client = storage.Client(credentials=get_credentials())

    blobs = storage_client.list_blobs(bucket_name)

    for blob in blobs:
        
        if(blob.name[-1] == '/'):
            continue

        print("PRINTING blob : ", blob.name)
        # url = blob.generate_signed_url(
        # version="v4",
        # # This URL is valid for 15 minutes
        # expiration=datetime.timedelta(minutes=15),
        # # Allow GET requests using this URL.
        # method="GET",
        # credentials=get_credentials()
        # )
        # result.append(url)
        
    return result

print(generate_object_urls())
