import vertexai
import os
from dotenv import load_dotenv
from vertexai.generative_models import GenerativeModel, Part
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

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

signed_urls = generate_object_urls()

print(signed_urls)

print(get_response("what is blue"))