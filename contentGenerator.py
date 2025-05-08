# gemini_client.py
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import base64
import os
import json
import re
import streamlit as st
import requests

# Set API key (ensure this is available in your environment)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# ===================== 1. Slide Generator using Gemini 1.5 Flash =====================
def generate_slide_deck(topic: str):
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
You are an educational assistant.

Take this input: “{topic}”

Generate an educational carrousel broken into 10-15 slides. Make it interesting like a game or a story, 
gor eg: Ask a interesting question in the first slide, and then with every slide keep giving more information and take the reader 
closer to the answer. So that the reader does not lose interest. 

For each slide, provide:
1. Slide title
2. Important info as bullet points with max 25 words each. Use complete sentences not clauses. (total ≤ 60 words)
3. A visual prompt for a cartoon-style image with no background

Respond in structured JSON format:
[
  {{
    "slide": 1,
    "title": "...",
    "bullets": ["...", "..."],
    "visual_prompt": "..."
  }},
  ...
]
"""

    response = model.generate_content(prompt)
    raw_output = response.text.strip()

    # Try to parse JSON directly
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        # Try to recover a JSON-looking array
        match = re.search(r'\[\s*{.*}\s*\]', raw_output, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                return []
    return []

# ===================== 2. Image Generator using Gemini 2.0 Flash (Experimental) =====================
def generate_image_from_prompt(prompt: str) -> str:
    """
    Generates an image using Gemini 2.0 Flash experimental image generation via REST.
    Returns the image as a base64-encoded string.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY environment variable")

    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp-image-generation:generateContent?key={api_key}"

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"]
        }
    }

    try:
        response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()

        for candidate in data.get("candidates", []):
            for part in candidate["content"].get("parts", []):
                if "inlineData" in part and "data" in part["inlineData"]:
                    return part["inlineData"]["data"]  # base64 string

    except Exception as e:
        print(f"[Image Generation Error] {e}")

    return None
