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

def generate_object_urls(bucket_name, credentials):
    
    result = []
    storage_client = storage.Client(bucket_name, credentials)
    blobs = storage_client.list_blobs(bucket_name)

    for blob in blobs:

        if(blob.name[-1] == '/'):
            continue
        print(blob.name)
        # if(".pdf" in blob.name.lower()):
        #     print(blob.name)
            # url = f"gs://{bucket_name}/{blob.name}"
        url = blob.generate_signed_url(
            version="v4",
            # This URL is valid for 15 minutes
            expiration=datetime.timedelta(days=7),
            # Allow GET requests using this URL.
            method="GET",
            credentials=get_credentials()
            )
        
        result.append(url)

    return result

def adjustURL(url : str) -> str:
    """
    utility function to trim the signed url to store in BigQuery Table
    """
    segment = url.split('?',2)[0]
    res = segment.split('/',5)[-1]
    return res

print(generate_object_urls("earthquake_bukt", get_credentials()))
# print(adjustURL("https://storage.googleapis.com/earthquake_bukt/test/page104.pdf?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=khantnhl%40gen-lang-client-0175492774.iam.gserviceaccount.com%2F20250708%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20250708T190547Z&X-Goog-Expires=900&X-Goog-SignedHeaders=host&X-Goog-Signature=a6d9e5c37d88f5bb6e06f856ba49a3e944f1a86b621b3539d52d3f95c9cf0500c234b34c08340f89da0ec6dbfddbd175536367b54b3d4d16b8e4fec5ae3827fbd8e8a74b0afe2dff6b449ae14837a2c035c23b6dd1f6d5a643d241e974d6b2f3b152acbfc0a6d8238eab51ea86c5d805584dfec5fd2fdd1920c5128fac1791cbcd322ca3a5f2123f2610c7ad03728cc477a647858c1909957843ea8c18b6baa1df2d3e6ab28157027738b276deb8ea7ef9d4b71db34cdf2bd939a7e493f5a8ef5684424e575f564faf10ae624cedd85a39ad74c21f446af47611cb75418d1e9b1ffd93e1637d0f0319c76a579cda812ae0322eef8b60e4f6ab81e14397d40210"))