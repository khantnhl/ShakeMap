import vertexai
import os
from dotenv import load_dotenv
from vertexai.generative_models import GenerativeModel, Part
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.cloud import bigquery
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'processors'))
from processors.multimodalroutes import multimodalRouter
from services.credentialUtils import get_credentials
from services.gcloudUtil import generate_object_urls
from manage_model import get_response

load_dotenv()

path = os.environ['filepath']
projectID = os.environ['projectID']

credentials = Credentials.from_service_account_file(path, scopes=["https://www.googleapis.com/auth/cloud-platform"])
if credentials.expired:
    credentials.refresh(Request())

vertexai.init(project=projectID, location='us-central1', credentials=credentials)

client = bigquery.Client(project=projectID)

query = """
    SELECT *
    FROM `gen-lang-client-0175492774.earthquake_dataset.url_table`
"""

rows = client.query_and_wait(query)  # Make an API request.

signed_urls = []
video_urls = []
image_without_location = []

for row in rows:
    if("pdf" in row["signed_url"]):
        signed_urls.append((row["blob_name"], row["signed_url"]))
    elif("jpg" in row["signed_url"] or "jpeg" in row["signed_url"]):
        image_without_location.append((row["blob_name"], row["signed_url"]))
    elif("mp4" in row["signed_url"]):
        video_urls.append((row["blob_name"], row["signed_url"]))

print("size: ", len(signed_urls))
print("size: ", len(image_without_location))
print("size: ", len(video_urls))

modalRouter = multimodalRouter()

# signed_url is tuple (blob_name, signedurl)
for i, url in enumerate(video_urls):

        response = modalRouter.get_type_and_generate(url[0], url[1])
        print(f"Processing {i}")
        with open("temp.json", "a") as f:
            f.write(json.dumps(response, indent=4) + ",\n")


print("Done")