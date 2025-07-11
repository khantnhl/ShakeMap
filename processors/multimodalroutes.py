from manage_model import get_response
from vertexai.generative_models import GenerativeModel, Part

def getType(signed_url):
    # determine mime type
    mimeType = None
    if(".jpg" in signed_url.lower()):
        mimeType = "image/jpg"
    elif(".mp4" in signed_url.lower()):
        mimeType = "video/mp4"
    elif(".pdf" in signed_url.lower()):
        mimeType = "application/pdf"
    
    return mimeType

def getImageDetails(signed_url):
    """
    Prepare Image + prompt for response 
    """
    contents = []
    imageDescription_Prompt = "Describe the image in detail."
    contents = [imageDescription_Prompt, Part.from_uri(signed_url, mime_type=getType(signed_url))]
    return get_response(contents)

def getVideoDetails(signed_url):
    """
    Prepare Video + prompt for response
    """
    contents = []
    videoDescription_Prompt = "Describe the video in detail."
    contents = [videoDescription_Prompt, Part.from_uri(signed_url, mime_type=getType(signed_url))]
    return get_response(contents)

