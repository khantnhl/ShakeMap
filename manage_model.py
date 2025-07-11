import vertexai
import os
from dotenv import load_dotenv
from vertexai.generative_models import GenerativeModel, Part
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from services.gcloudUtil import generate_download_signed_url_v4, generate_object_urls
from config.gemini_config import geminiConfig, sf_settings

load_dotenv()

path = os.environ['filepath']
projectID = os.environ['projectID']

credentials = Credentials.from_service_account_file(path, scopes=["https://www.googleapis.com/auth/cloud-platform"])
if credentials.expired:
    credentials.refresh(Request())

vertexai.init(project=projectID, location='us-central1', credentials=credentials)

def get_model():
    global model_init
    if(not model_init):
        model_init = GenerativeModel("gemini-2.5-flash")
    return model_init

def get_response(contents: list):

    model = get_model()
    response = model.generate_content(
                    generation_config=geminiConfig, 
                    safety_settings=sf_settings, 
                    contents=contents,    
                    stream=False
                    )
        
    return response.text

# # mandalay
# event_record = {
#     "mag" : 7.7,
#     "latLng" : [22.011, 95.936]
# }

# OUTPUT Prompts 
from prompts.prompts import location_prompt, output_prompt

# queue
signed_urls = generate_object_urls()

result = []

for i, url in enumerate(signed_urls):
    print(f"Processing {i + 1} :")

    if(i == 0): 
        context_for_gemini = [
        location_prompt,
        output_prompt   
        ]
        
        # determine mime type
        mimeType = None
        if(".jpg" in url.lower()):
            mimeType = "image/jpg"
        elif(".mp4" in url.lower()):
            mimeType = "video/mp4"
        elif(".pdf" in url.lower()):
            mimeType = "application/pdf"
        if(mimeType):
            context_for_gemini.append(Part.from_uri(url, mime_type=mimeType))
        else:
            raise TypeError("Invalid FileType Object")

    try: 
        response = model.generate_content(
                    generation_config=geminiConfig, 
                    safety_settings=sf_settings, 
                    contents=context_for_gemini,    
                    stream=False
                    )
        
        # print(f"{i+1} Output : {response.text}")
        result.append(response.text)
    except Exception as e:
        print(f"{e}")
        
        print(result[0])
