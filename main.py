import vertexai
import os
import json
from dotenv import load_dotenv
from vertexai.generative_models import GenerativeModel, GenerationConfig, Image, SafetySetting, HarmCategory, HarmBlockThreshold, Part
from google.genai.types import Tool, GenerateContentConfig
from google.genai import types
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from gcloudUtil import generate_download_signed_url_v4, generate_object_urls

load_dotenv()

path = os.environ['filepath']
projectID = os.environ['projectID']

credentials = Credentials.from_service_account_file(
    path, 
    scopes=["https://www.googleapis.com/auth/cloud-platform"])

if credentials.expired:
    credentials.refresh(Request())

vertexai.init(project=projectID, location='us-central1', credentials=credentials)

config= GenerationConfig(
        temperature=0.4,
        top_p=0.95,
        top_k=20,
        candidate_count=1,
        seed=5,
        max_output_tokens=8100,
        stop_sequences=["STOP!"],
        presence_penalty=0.0,
        frequency_penalty=0.0,
        response_logprobs=False,  # Set to True to get logprobs, Note this can only be run once per day
        response_mime_type="application/json"
    )

sf_settings = [
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    ),
]

url_context_tool = Tool(url_context = types.UrlContext)

model = GenerativeModel("gemini-2.5-flash")

event_record = {
    "mag" : 7.7,
    "latLng" : [22.011, 95.936]
}

# OUTPUT Prompts 
from prompts import location_prompt, output_prompt

# response = model.generate_content(
#     generation_config=config, 
#     safety_settings=sf_settings, 
#     contents=location_prompt,    
#     stream=False
#     )

# print(response.text)

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
                        generation_config=config, 
                        safety_settings=sf_settings, 
                        contents=context_for_gemini,    
                        stream=False
                        )
            
            json_output = json.loads(response.text)

            result.append(json_output)
        except json.JSONDecodeError as e:
            print(f"Error: Failed to decode JSON from model response for URL: {url}. Error: {e}")
        except Exception as e:
            print(f"{e}")
        
        print(result[0])


# To-Do Tasks
# generate intensities 
# with known locations from Steer Report
# use the MMI reference
# keep record of prompts and things I changed