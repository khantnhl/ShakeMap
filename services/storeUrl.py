import sys
import os
import json
from dotenv import load_dotenv
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
from google.cloud import storage, bigquery
from credentialUtils import get_credentials
from gcloudUtil import generate_object_urls, adjustURL
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.gemini_config import geminiConfig, sf_settings
from prompts.prompts import tablePrompt

load_dotenv()

path = os.environ['filepath']
projectID = os.environ['projectID']

BASE_DIR = os.path.dirname(__file__)
path = os.path.join(BASE_DIR, "../gen-lang-service-keys.json")  # adjust if file is elsewhere

credentials = Credentials.from_service_account_file(
    path, 
    scopes=["https://www.googleapis.com/auth/cloud-platform"])

if credentials.expired:
    credentials.refresh(Request())

vertexai.init(project=projectID, location='us-central1', credentials=credentials)

model = GenerativeModel("gemini-2.5-flash")


storage_client = storage.Client(project="gen-lang-client-0175492774", credentials=get_credentials())
bigquery_client = bigquery.Client(project="gen-lang-client-0175492774", credentials=get_credentials())

table_schema = [
    bigquery.SchemaField("blob_name", "STRING", description="FileName"),
    bigquery.SchemaField("signed_url", "STRING", description="url")
]

datasetID = "gen-lang-client-0175492774.earthquake_dataset"
try: 
    bigquery_client.get_dataset(dataset_ref=datasetID)
    print("dataset exists")
except:
    dataset = bigquery.Dataset(dataset_ref=datasetID)
    dataset.location = "US"
    dataset = bigquery_client.create_dataset(dataset)
    print(f"Dataset Created..")

tableID = "gen-lang-client-0175492774.earthquake_dataset.url_table"
# tableID = "gen-lang-client-0175492774.earthquake_dataset.image_descriptions"

try:
    table = bigquery_client.get_table(tableID)
    print("Table exists..")
except:
    table = bigquery.Table(tableID, schema=table_schema)
    table = bigquery_client.create_table(table)
    print(f"Created {table.table_id}")

try: 
    urls = generate_object_urls("earthquake_bukt", get_credentials())
    print("Status: Generated Object Signed URLs")

except:
    print("Error generating signed urls")

insertRows = []


try: 
    for i, url in enumerate(urls):
        
        print(f"Processing : {i}")
        insertRows.append({"blob_name" : adjustURL(url), 
                        "signed_url" : url
                        })
    
    bigquery_client.insert_rows_json(tableID, insertRows)
    print("Successfully Inserted..")
except:
    raise RuntimeError("Failed to Insert to table..")
