import vertexai
import os
from dotenv import load_dotenv
from vertexai.generative_models import GenerativeModel, Part
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from config.gemini_config import geminiConfig, sf_settings
from functools import lru_cache

@lru_cache
def get_model():
        return GenerativeModel("gemini-2.5-flash")

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

