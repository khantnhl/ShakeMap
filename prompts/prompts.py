location_prompt="""
                    Analyse the provided image/video and extract any information that indicates the location of the user or post. 
                    Identify the specific location name, including city, state (if applicable) and country. 
                    Limit your response only to the extracted location. Example output: Imperial, CA
                """

# Few-Shot Prompting
output_prompt = """
Generate a JSON output based on the analysis of the provided image/video and any accompanying textual information.
The JSON output MUST strictly follow this exact structure and keys:

```json
{
    "felt by user": "Yes/No/Unspecified",
    "class source": "e.g., Surveillance Footage (YouTube), Social Media (X/Twitter), News Report, User Submission",
    "post location": "Specific location (City, State, Country) derived from post/video, e.g., Boonton, NJ",
    "post date time": "Exact date and time if available, e.g., April 5, 2024 (exact time not specified)",
    "earthquake location": "Geographical area of the earthquake, e.g., North-east U.S. (N18V)",
    "earthquake magnitude": "Numeric magnitude, e.g., 4.8 (provided in video description)",
    "distance to earthquake epicentre": "Numeric distance and unit, e.g., 37.59 km (provided by user)",
    "shaking duration": "Observed duration, e.g., Several seconds, as observed in the video footage",
    "building type": "e.g., Coffee shop (commercial building), Residential home, Office building",
    "building materials": "e.g., Concrete, Wood, Brick, Unknown",
    "human reaction": "Detailed description of human behavior and emotional state",
    "animals reaction": "Description of animal behavior, or 'Not visible in the video'",
    "furnishing": "List of visible items, e.g., Tables, chairs, light fixtures",
    "language": "Primary language detected in audio/text, e.g., English",
    "natural environment": "Description of natural surroundings, or 'Not visible in the video'",
    "video evidence": {
        "Object Movement": "Description of moving objects and their significance.",
        "People Running and Seeking Cover": "Description of people's panicked behavior.",
        "Limited Object Falling": "Description of falling objects and their extent."
    },
    "audio evidence": {
        "Sounds of Distress": "Description of vocal expressions of fear.",
        "Background Noise": "Description of ambient sounds."
    },
    "textual evidence": {
        "Video Description": "Information from video descriptions.",
        "News Overlay": "Information from news tickers or overlays."
    },
    "mmi estimation": "MMI level (e.g., MMI IV or MMI V)",
    "mid mmi value numeric": "Numeric average or representative MMI value, e.g., 4.5",
    "estimation confidence": "Numeric confidence score (0.0 to 1.0), e.g., 0.7",
    "visual observation": "Detailed explanation of visual cues supporting MMI.",
    "auditory cues": "Detailed explanation of auditory cues supporting MMI.",
    "textual information": "Detailed explanation of textual cues supporting MMI.",
    "analysis of evidences": "Comprehensive analysis combining all evidence types.",
    "reasoning": "Explanation for the MMI estimation based on all observations."
}
"""

# Chain-Of-Thought
tablePrompt = """
You are an expert image analyzer. For the given image, do the following:

1. Describe everything you can see in the image in rich detail in one long sentence.
2. If any location information is visible (e.g., street signs, popular buildings), infer and extract it.
3. If there's no explicit text showing a location, give your best guess based on visual clues.

Strictly Return the output in the following format:

{
    "description": <Full detailed description",
    "location" : <inferred location or Unknown>
}
"""