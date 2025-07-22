from manage_model import get_response
from vertexai.generative_models import Part
import json, re
from MMIRetriever import MMIRetriever
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

schemas = [
    ResponseSchema(name="blob_name", description="Name of the object"),
    ResponseSchema(name="description", description="Detailed description of earthquake damages"),
    ResponseSchema(name="location", description="Location dictionary with 'address' and 'coordinates'"),
    ResponseSchema(name="auditory_cues", description="Summary of sounds indicating seismic activity"),
    ResponseSchema(name="background_noise", description="Ambient sounds in the environment"),
    ResponseSchema(name="sounds_of_distress", description="Human reactions or cries"),
    ResponseSchema(name="visual_observation", description="Objects or structural damage seen"),
    ResponseSchema(name="video_evidence", description="Key video frames suggesting shaking"),
    ResponseSchema(name="building_type", description="Type of building involved"),
    ResponseSchema(name="building_materials", description="Visible construction materials"),
    ResponseSchema(name="evidence_analysis", description="Final analysis for MMI reasoning"),
    ResponseSchema(name="context_summary", description="Summary of all context and cues"),
    ResponseSchema(name="mmi_estimation", description="Estimated MMI value", type="number"),
    ResponseSchema(name="reasoning", description="Step-by-step reasoning for MMI"),
    ResponseSchema(name="confidence", description="Confidence score from 0.0 to 1.0")
]
parser = StructuredOutputParser.from_response_schemas(schemas)

class multimodalRouter:
    def __init__(self):
        pass
    
    def get_type_and_generate(self, blob_name, signed_url):
        # determine mime type
        mimeType = None
        if(".pdf" in signed_url.lower()):
            mimeType = "application/pdf"
            return self.getDetails(blob_name, signed_url, mimeType)
        elif(".mp4" in signed_url.lower()):
            mimeType = "video/mp4"
            return self.getDetails(blob_name, signed_url, mimeType)
        else:
            raise ValueError("Undefined mime_type")
 
    
    # Zero-shot prompting
    def getDetails(self, blob_name, signed_url, type):
        """
        Prepare Image + Video prompt for response 
        """
        contents = []
        Description_Prompt = f"""
            <System Prompt>
            You are an expert seismologist, studying earthquake impact using the Modified Mercalli Intensity Scale (MMI). 
            Your task is to carefully analyze image or video evidence to identify visual and auditory indicators of shaking intensity.
            </System Prompt>

            Describe the contents of the image or video in detail.
            Your response must be a valid JSON object containing the following fields:

            {{
                "blob_name": "{blob_name}",
                "description": "Detailed textual description of damages and casualties in the image/video.",
                "location": {{
                    "address": "Mandalay Hospital, Mandalay City, Myanmar" OR "Unknown" if not found,
                    "coordinates": [latitude, longitude] or [0.0, 0.0] if not found
                }},
                "auditory_cues": "The audio evidence supports the visual observations, with people’s vocal expressions of fear and distress indicating a level of alarm consistent with moderate shaking.",
                "background_noise": "General coffee shop ambiance and potential sounds of objects rattling or moving.",
                "sounds_of_distress": "People expressing fear and concern, with exclamations like ‘Earthquake!’ and ‘Mommy!’",
                "visual_observation": "List visible elements such as shaking objects, cracked walls, crowds, smoke, etc.",
                "video_evidence": "Summarize key visual cues that confirm seismic activity (e.g., light fixtures swaying, debris falling).",
                "building_type": "Type of building affected (e.g., residential, hospital, commercial).",
                "building_materials": "Construction materials visible in the structure (e.g., brick, concrete, wood, bamboo).",
                "evidence_analysis": "The combined evidence from visual, auditory, and textual sources points to an earthquake intensity in the range of MMI IV to MMI V at the coffee shop location. The observed effects align with the characteristics of these MMI levels, where objects move notably, people feel frightened and react, but significant damage is not widespread."
            }}
            """
        contents = [Part.from_text(Description_Prompt), Part.from_uri(signed_url, mime_type=type)]
        firstResponse = get_response(contents)
        
        # second 
        format_instructions = parser.get_format_instructions()

        secondPrompt = f"""
        Given this description:
        (1) Summarize the data (e.g. shaking duration, reactions);
        (2) Organize visual, auditory, and textual evidence;
        (3) Estimate MMI value (must be in float);
        (4) Explain your reasoning;
        (5) Note model limitations.

        Your response must follow this format:
        {format_instructions}
        """
        secondcontents = [Part.from_text(secondPrompt), Part.from_text(firstResponse)]
        secondResponse = get_response(secondcontents)

        secondObj = parser.parse(secondResponse)
        mmi_retriever = MMIRetriever()
        mmis = mmi_retriever.retrieve(secondObj["context_summary"])
        secondObj["mmi_semantic"] = [mmis]

        return secondObj
        

