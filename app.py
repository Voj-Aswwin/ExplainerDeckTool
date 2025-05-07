from flask import Flask, request, render_template, send_file
from fpdf import FPDF
from gemini_client import generate_slide_deck, generate_image_from_prompt
import base64
import os

class PDF(FPDF):
    def header(self):
        self.add_font("Noto", "", "fonts/NotoSans-Regular.ttf", uni=True)
        self.set_font("Noto", "", 12)
        self.cell(0, 10, "AI Slide Deck", ln=True, align="C")

    def add_slide(self, title, bullets, image_base64):
        self.add_page()
        self.add_font("Noto", "", "fonts/NotoSans-Regular.ttf", uni=True)
        self.set_font("Noto", "", 12)
        self.cell(0, 10, title, ln=True)
        self.ln(5)
        for b in bullets:
            self.cell(0, 8, f"• {b}", ln=True)
        if image_base64:
            image_path = "/tmp/temp_image.png"
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(image_base64))
            self.image(image_path, x=130, y=30, w=60)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    slides = []
    topic = ""

    if request.method == "POST":
        topic = request.form["topic"]
        raw_slides = generate_slide_deck(topic)

        slides = []
        for slide in raw_slides:
            image_data = generate_image_from_prompt(slide["visual_prompt"])
            slide["image_base64"] = image_data
            slides.append(slide)

    return render_template("index.html", slides=slides, topic=topic)

@app.route("/generate_pdf")
def generate_pdf():
    topic = request.args.get("topic", "")
    slides = generate_slide_deck(topic)

    pdf = PDF()
    for slide in slides:
        image_data = generate_image_from_prompt(f"{slide['visual_prompt']}, cartoon style, no background, transparent PNG")
        pdf.add_slide(slide["title"], slide["bullets"], image_data)

    output_path = "/tmp/slide_deck.pdf"
    pdf.output(output_path)
    return send_file(output_path, as_attachment=True, download_name="slide_deck.pdf")


if __name__ == "__main__":
    app.run(debug=True)
