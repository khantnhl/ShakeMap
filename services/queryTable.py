from google.cloud import storage, bigquery
from credentialUtils import get_credentials
from gcloudUtil import generate_object_urls, adjustURL
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

client = bigquery.Client()

query = """
    SELECT *
    FROM `gen-lang-client-0175492774.earthquake_dataset.image_descriptions`
"""
rows = client.query_and_wait(query)  # Make an API request.

print("The query data:")
for row in rows:
    print(row["signed_url"])

    break