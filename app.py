import streamlit as st
from contentGenerator import generate_slide_deck, generate_image_from_prompt
import base64
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="📘 Learn In Slides", layout="wide")

st.markdown("""
    <style>
        .slide-box {
            max-width: 900px;
            margin: auto;
            background-color: #f9f9f9;
            padding: 2rem;
            border-radius: 1rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .slide-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        .slide-bullet {
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
        }
        .slide-footer {
            text-align: center;
            font-style: italic;
            margin-top: 1rem;
            color: grey;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>📘 Learn in Slides</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Turn any concept into a 15-slide visual lesson</p>", unsafe_allow_html=True)
st.markdown("---")

if "slides" not in st.session_state:
    st.session_state.slides = []
if "current_slide" not in st.session_state:
    st.session_state.current_slide = 0

topic = st.text_input("🔍 What concept do you want to learn?", placeholder="e.g. Thermodynamics, Harappan Civilization")

if st.button("🚀 Generate Full Slide Deck"):
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        with st.spinner(" 🎨🖌️ Generating full slide deck with illustrations... please wait ⏳"):
            slides = generate_slide_deck(topic)
            if not slides:
                st.error("❌ Failed to generate slide content. Please try again.")
            else:
                for slide in slides:
                    img_data = generate_image_from_prompt(slide['visual_prompt'])
                    slide['image'] = img_data
                st.session_state.slides = slides
                st.session_state.current_slide = 0

slides = st.session_state.slides
if slides:
    st.success(f"✅ Your deck on **{topic}** is ready!")

    # Slide Navigation Buttons
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("⬅️ Previous") and st.session_state.current_slide > 0:
            st.session_state.current_slide -= 1
    with col3:
        if st.button("➡️ Next") and st.session_state.current_slide < len(slides) - 1:
            st.session_state.current_slide += 1

    slide = slides[st.session_state.current_slide]
    col_text, col_image = st.columns([2, 1])

    with col_text:
        st.markdown(f"### {slide['slide']}. {slide['title']}")
        for bullet in slide['bullets']:
            st.markdown(f"- {bullet}")

    with col_image:
        if slide.get('image'):
            st.image(base64.b64decode(slide['image']), use_container_width=True)
        else:
            st.info("Image not available for this slide.")

    st.markdown(f"<p style='text-align: center;'>Slide {st.session_state.current_slide + 1} of {len(slides)}</p>", unsafe_allow_html=True)

st.markdown("---")
st.caption("🔬 Powered by Gemini • Built by Voj")
