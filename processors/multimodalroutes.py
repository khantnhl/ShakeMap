from manage_model import get_response
from vertexai.generative_models import Part

class multimodalRouter:
    def __init__(self):
        pass

    def get_type_and_generate(self, signed_url):
        # determine mime type
        mimeType = None
        if(".jpg" in signed_url.lower()):
            mimeType = "image/jpg"
            return self.getImageDetails(signed_url, mimeType)
            
        elif(".mp4" in signed_url.lower()):
            mimeType = "video/mp4"
            return self.getVideoDetails(signed_url, mimeType)
        elif(".pdf" in signed_url.lower()):
            mimeType = "application/pdf"
            return self.getImageDetails(signed_url, mimeType)
        else:
            raise ValueError("Undefined mime_type")
 

    def getImageDetails(self, signed_url, type):
        """
        Prepare Image + prompt for response 
        """
        contents = []
        imageDescription_Prompt = """
        Describe the image in detail.
        Your response must be a JSON object containing 2 fields: description and location. It has the following schema:
 
        * description : Detailed description of earthquake damages, casualities  in the image 
        * location : { "address": "Mandalay Hospital, Mandalay City, Myanmar" OR "Unknown" if it is not found, 
                        "coordinates": [latitude, longitude] or [0.0, 0.0] if not found} } 
        """
        contents = [imageDescription_Prompt, Part.from_uri(signed_url, mime_type=type)]
        return get_response(contents)

    def getVideoDetails(self, signed_url, type):
        """
        Prepare Video + prompt for response
        """
        contents = []
        videoDescription_Prompt = """Describe the video in detail on what is happening.
        Your response must be a JSON object containing 2 fields: description and location. It has the following schema:
 
        * description : Detailed description of earthquake damages, casualities  in the video 
        * location : { "address": "Mandalay Hospital, Mandalay City, Myanmar", "coordinates": [latitude, longitude] } }"""
        contents = [videoDescription_Prompt, Part.from_uri(signed_url, mime_type=type)]
        return get_response(contents)

