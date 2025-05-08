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
You are a storytelling educator.

Take this input: “{topic}”

You need to educate the reader about this concept.

Create a story-driven educational carousel in 15–20 slides. The story must centre around a fictional protagonist facing a problem 
and solving that problem by exploring a real concept related to the topic. Through each slide, the character learns, explores or struggles. 
The user (reader) follows along, engaging emotionally and intellectually.

Each slide must:
- Use story to emotionally engage
- Introduce or explain one key learning insight
- Optionally ask a question — but if a question is asked, the *very next slide must answer it clearly*

For each slide, provide:
1. Slide Title — short and engaging
2. Bullets (≤ 90 words total): 
   - Line 1: Story moment
   - Line 2: Learning point or key fact
   - Line 3 (optional): A question — but ONLY if the next slide answers it
3. For the visual prompt:
    - Describe a cartoon-style scene with no background
    - If the subject includes a real person or a scientific/technical concept, request a **hyper-realistic** visual
    - Do **not** include written text, signs, documents with visible letters, or any symbols with text

Assume the reader is new to this topic. So Use very simple terms and analogies wherever applicable. 
And avoid using Jargons or complex sentences
    
Final slide: summarise the protagonist’s journey and clearly state what the reader has learned or understood.

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
