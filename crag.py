import os
import vertexai
import json
from typing import List, Dict, Any
from typing_extensions import TypedDict

from vertexai.generative_models import Part
from processors.MMIRetriever import MMIRetriever

from manage_model import get_response, get_model
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import START, END, StateGraph

from pprint import pprint

load_dotenv()

path = os.environ['filepath']
projectID = os.environ['projectID']
TRAVILY_API_KEY = os.environ['TAVILY_API_KEY']

credentials = Credentials.from_service_account_file(path, scopes=["https://www.googleapis.com/auth/cloud-platform"])
if credentials.expired:
    credentials.refresh(Request())

vertexai.init(project=projectID, location='us-central1', credentials=credentials)

class State(TypedDict):
    """
    State of our graph

    Attributes: 
        **blob_name : name of media file
        **signed_url
        **initial_analysis : first-pass analysis to LLM
        **context_summary : Summary of earthquake context
        **mmi_documents : Retrieved seismic reference documents
        **web_search : Whether to perform web search for additional context
        **final_analysis : final formatted response
    """
    blob_name : str
    signed_url : str
    mime_type : str
    initial_analysis : str
    context_summary : str
    mmi_documents : List[Document]
    web_search : str
    final_analysis : Dict[str, Any]
    generation : str

GRADE_DOCUMENTS_SCHEMA = {
    "type": "object",
    "properties": {
        "binary_score": {
            "type": "string",
            "description": "Documents are relevant to earthquake assessment, 'yes' or 'no'",
            "enum": ["yes", "no"]
        }
    },
    "required": ["binary_score"]
}

SEISMIC_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "blob_name": {"type": "string"},
        "description": {"type": "string"},
        "location": {
            "type": "object",
            "properties": {
                "address": {"type": "string"},
                "coordinates": {"type": "array", "items": {"type": "number"}}
            }
        },
        "auditory_cues": {"type": "string"},
        "background_noise": {"type": "string"},
        "sounds_of_distress": {"type": "string"},
        "visual_observation": {"type": "string"},
        "video_evidence": {"type": "string"},
        "building_type": {"type": "string"},
        "building_materials": {"type": "string"},
        "evidence_analysis": {"type": "string"},
        "context_summary": {"type": "string"},
        "mmi_estimation": {"type": "number"},
        "reasoning": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0}
    },
    "required": ["blob_name", "description", "location", "mmi_estimation", "reasoning", "confidence"]
}


class MultimodalEarthquakeCRAG:
    def __init__(self):
        self.mmi_retriever = MMIRetriever()
        self.web_search_tool = TavilySearchResults(k=3,TAVILY_API_KEY=TRAVILY_API_KEY)
        self.setup_graph()

    def setup_graph(self):
        workflow = StateGraph(State)
        workflow.add_node("initial_analysis", self.initial_analysis)
        workflow.add_node("retrieve_docs", self.retrieve_docs)
        workflow.add_node("grade_documents", self.grade_documents)
        workflow.add_node("web_search", self.web_search)
        workflow.add_node("transform_query", self.transform_query)
        workflow.add_node("final_analysis", self.final_analysis)

        workflow.add_edge(START, "initial_analysis")
        workflow.add_edge("initial_analysis", "retrieve_docs")
        workflow.add_edge("retrieve_docs", "grade_documents")
        workflow.add_conditional_edges(
                    "grade_documents",
                    self.decide_to_analyze,
                    {
                        "transform_query": "transform_query",
                        "final_analysis": "final_analysis",
                    },
                )
        workflow.add_edge("transform_query", "web_search")
        workflow.add_edge("web_search", "final_analysis")
        workflow.add_edge("final_analysis", END)

        self.app = workflow.compile()

    
    def analyze_media_and_traverse_states(self, blob_name : str, signed_url : str, mime_type : str):
        if ".pdf" in signed_url.lower():
            mime_type = "application/pdf"
        elif ".mp4" in signed_url.lower():
            mime_type = "video/mp4"
        else:
            raise ValueError("Unable to determine mime type from URL")
        
        # inital state
        inputs = {
            "blob_name": blob_name,
            "signed_url": signed_url,
            "mime_type": mime_type
        }
        
        for output in self.app.stream(inputs):
            for key, value in output.items():
                # Node
                pprint(f"Node '{key}':")
                # Optional: print full state at each node
                pprint(value, indent=2, width=80, depth=None)
            pprint("\n---\n")
       
        return value
    
    def get_structured_response(self, contents : list, response_schema):
        """Get structured response from Gemini using JSON schema."""
        
        # Add schema instructions to the content
        schema_prompt = f"""
        Please respond with a valid JSON object that matches this exact schema:
        {json.dumps(response_schema, indent=2)}
        
        Ensure all required fields are included and data types match the schema.
        """
        
        # Combine schema prompt with original contents
        full_contents = [Part.from_text(schema_prompt)] + contents
        
        response = get_response(full_contents)
        
        # Parse JSON response
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise ValueError(f"Could not parse JSON from response: {response}")

    def decide_to_analyze(self, state):
        """Decide whether to proceed with analysis or search for more documents."""
        print("---ASSESS GRADED DOCUMENTS---")
        web_search = state["web_search"]
        
        if web_search == "Yes":
            print("---DECISION: INSUFFICIENT RELEVANT DOCUMENTS, SEARCH FOR MORE---")
            return "transform_query"
        else:
            print("---DECISION: SUFFICIENT DOCUMENTS, PROCEED TO ANALYSIS---")
            return "final_analysis"
    
    def initial_analysis(self, state):
        blob_name = state["blob_name"]
        signed_url = state["signed_url"]
        mime_type = state["mime_type"]

        Description_Prompt = f"""
            <System Prompt>
            You are an expert seismologist, studying earthquake impact using the Modified Mercalli Intensity Scale (MMI). 
            Your task is to carefully analyze image or video evidence to identify visual and auditory indicators of seismic shaking.
            Avoid making assumptions or what is not visible or audible in the media. 
            Carefully analyze and describe the contents of the image or video in detail.
            </System Prompt>

            For images 
                - Look for visible surface damage, collapsed buildings, cracks, dust clouds, displaced infrastructure.
                - If it's a satellite or aerial view, analyze top-down damage: roof collapses, ruptured roads, debris zones, or displaced land features.
            For videos
                - Detect dynamic events such as shaking lights, falling debris, swaying structures, ground rupture, or displacement.
                - Audio may be absent but it does not mean there is no earthquake
                - If audio is present, analyze for screams, panic, structural sounds (crashing, creaking), or silence after impact.
        """
        
        contents = [
            Part.from_text(Description_Prompt),
            Part.from_uri(signed_url, mime_type=mime_type)
        ]
        analysis = get_response(contents)

        return {
            "blob_name": blob_name,
            "signed_url": signed_url,
            "mime_type": mime_type,
            "initial_analysis": analysis,
            "context_summary": analysis # for retrieval
        }

    def retrieve_docs(self, state):
        print("---RETRIEVE MMI DOCUMENTS---")
        context = state["context_summary"]
        
        # retrieve from PineCone
        retrieved_docs = self.mmi_retriever.retrieveDocs(context)
        print("retrieved from PC: ", retrieved_docs)

        return {
            **state, 
            "mmi_documents": retrieved_docs
        }
    
    def grade_documents(self, state):
        print("---GRADE RETRIEVED DOCUMENTS---")

        context = state["context_summary"]
        documents = state["mmi_documents"]
        filtered_docs = []
        web_search = "No"

        for doc in documents:
            grader_prompt = f"""
                You are a grader assessing relevance of seismic/earthquake documents to earthquake damage assessment.
                If the document contains information about earthquake intensity scales (like MMI), building damage patterns,
                seismic indicators, or earthquake impact assessment, grade it as relevant.
                Retrieved document: {doc.page_content}
            Analysis context: {context}
            """

            contents = [Part.from_text(grader_prompt)]
            score = self.get_structured_response(contents, GRADE_DOCUMENTS_SCHEMA)

            if(score["binary_score"] == "yes"):
                print("---GRADE: DOCUMENT RELEVANT---")
                filtered_docs.append(doc)
            else:
                print("---GRADE: DOCUMENT NOT RELEVANT---")
                web_search = "Yes"
        
        return {
            **state, 
            "mmi_documents" : filtered_docs,
            "web_search" : web_search
        }

    def web_search(self, state):
        """Search web for additional seismic information."""
        print("---WEB SEARCH FOR SEISMIC INFO---")
        query = state["context_summary"]
        documents = state["seismic_documents"]
        
        # Perform web search
        search_results = self.web_search_tool.invoke({"query": f"earthquake intensity scale MMI damage assessment {query}"})
        web_content = "\n".join([result["content"] for result in search_results])
        web_doc = Document(page_content=web_content)
        
        documents.append(web_doc)
        
        return {
            **state,
            "seismic_documents": documents
        }

    def transform_query(self, state):
        """Transform query for better web search results using custom Gemini."""
        print("---TRANSFORM QUERY---")
        context = state["context_summary"]
        
        query_prompt = f"""
        You are a query optimizer for seismic information retrieval.
        Improve the earthquake assessment query to better find relevant seismic reference materials.
        
        Original context: {context}
        
        Provide an improved query for finding relevant earthquake intensity and damage assessment information.
        """
        
        contents = [Part.from_text(query_prompt)]
        better_query = get_response(contents)
        
        return {
            **state,
            "context_summary": better_query
        }
    
    def final_analysis(self, state):
        """Generate final seismic analysis with MMI estimation using custom Gemini."""
        print("---GENERATE FINAL SEISMIC ANALYSIS---")
        initial_analysis = state["initial_analysis"]
        documents = state["mmi_documents"]
        blob_name = state["blob_name"]
        
        # Format documents for analysis
        doc_context = "\n\n".join([doc.page_content for doc in documents])
        
        # Create final analysis prompt
        final_prompt = f"""
        You are an expert seismologist providing MMI assessment.
        Using the initial analysis and retrieved seismic reference documents, provide a complete assessment
        including MMI estimation with reasoning and confidence score.
        
        Initial Analysis: {initial_analysis}
        
        Reference Documents: {doc_context}
        
        Provide complete seismic analysis for {blob_name} including:
        - Detailed description of damages and observations
        - Location information (use "Unknown" if not determinable)  
        - Auditory and visual evidence summary
        - Building type and materials assessment
        - MMI estimation (as float) with detailed reasoning
        - Confidence score (0.0 to 1.0)
        """
        
        contents = [Part.from_text(final_prompt)]
        
        # Generate structured analysis using custom function
        analysis = self.get_structured_response(contents, SEISMIC_ANALYSIS_SCHEMA)
        
        # Format final 
        generation = f"""
        EARTHQUAKE ASSESSMENT REPORT
        ============================
        File: {analysis['blob_name']}
        MMI Estimation: {analysis['mmi_estimation']}
        Confidence: {analysis['confidence']}
        
        Description: {analysis['description']}
        Location: {analysis['location']}
        Building Type: {analysis['building_type']}
        Evidence Analysis: {analysis['evidence_analysis']}
        Reasoning: {analysis['reasoning']}
        """
        
        return {
            **state,
            "final_analysis": analysis,
            "generation": generation
        }

from google.cloud import bigquery
projectID = os.environ['projectID']

if __name__ == "__main__":
    
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

    # tuple (blob, signed_url)
    quake_CRAG = MultimodalEarthquakeCRAG()

    result = quake_CRAG.analyze_media_and_traverse_states(
        blob_name=signed_urls[0][0],
        signed_url=signed_urls[0][1],
        mime_type="application/pdf")
    
    print(result["generation"])
    with open("sample_test.txt", 'w') as f:
        f.write(result["generation"])

