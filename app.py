from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import cv2
import numpy as np
import os
import fitz
import logging
from flask_cors import CORS
from waitress import serve
import io
import re

# --- Basic Setup ---
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
CORS(app, resources={r"/*": {"origins": "*"}})

# --- Tesseract Path Configuration ---
pytesseract.pytesseract.tesseract_cmd = os.path.join(os.path.dirname(__file__), 'tesseract', 'tesseract.exe')

def preprocess_image(image):
    """
    Applies an advanced preprocessing pipeline to an image to make it suitable for OCR.
    """
    img_np = np.array(image)
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    
    scale_factor = 2
    width = int(gray.shape[1] * scale_factor)
    height = int(gray.shape[0] * scale_factor)
    resized = cv2.resize(gray, (width, height), interpolation=cv2.INTER_CUBIC)

    sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    sharpened = cv2.filter2D(resized, -1, sharpen_kernel)

    _, processed_img = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return processed_img

def detect_language(image):
    """
    Detects the dominant script in the image (Latin or Arabic) using Tesseract's OSD.
    """
    try:
        osd = pytesseract.image_to_osd(image, output_type=pytesseract.Output.DICT)
        script = osd.get('script')
        logging.info(f"Detected script: {script} (Confidence: {osd.get('sconf')})")
        
        if script == 'Arabic':
            return 'ara'
        elif script == 'Latin':
            return 'eng'
        else:
            return 'eng+ara' # Fallback
    except Exception as e:
        logging.error(f"Could not detect language due to error: {e}")
        return 'eng+ara' # Fallback

def post_process_text(text, lang):
    """
    Cleans the raw OCR output by filtering out nonsensical words and symbols.
    """
    # Split the raw text into individual words
    words = text.split()
    cleaned_words = []

    for word in words:
        # Rule 1: Define valid characters based on the detected language
        is_valid = False
        if lang == 'eng':
            # Allows English letters, numbers, and common punctuation within words (e.g., "don't", "state-of-the-art")
            if re.search(r'[a-zA-Z0-9]', word) and not re.match(r'^[^\w\s]+$', word):
                 is_valid = True
        elif lang == 'ara':
            # Allows Arabic letters and numbers.
            if re.search(r'[\u0600-\u06FF]', word) and not re.match(r'^[^\w\s]+$', word):
                is_valid = True
        else: # Fallback for mixed or undetermined language
             if re.search(r'[a-zA-Z0-9\u0600-\u06FF]', word) and not re.match(r'^[^\w\s]+$', word):
                is_valid = True

        # Rule 2: Check for minimum length (e.g., ignore single random characters)
        # We keep single letters 'a' and 'I' for English. You can customize this.
        min_length_check = True
        if len(word) == 1:
            if lang == 'eng' and word.lower() not in ['a', 'i']:
                min_length_check = False
            # Most single Arabic letters can be meaningful, so we allow them.
        
        if is_valid and min_length_check:
            cleaned_words.append(word)
    
    return ' '.join(cleaned_words)


@app.route('/ocr', methods=['POST'])
def ocr():
    """Generic OCR endpoint for processing image files."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        image = Image.open(file.stream).convert("RGB")
        processed_image = preprocess_image(image)
        
        lang = detect_language(processed_image)
        logging.info(f"Using language model: {lang}")
        
        custom_config = f'-l {lang} --oem 3 --psm 6'
        raw_text = pytesseract.image_to_string(processed_image, config=custom_config)
        
        cleaned_text = post_process_text(raw_text, lang)
        
        return jsonify({'text': cleaned_text})
    except Exception as e:
        logging.error("An error occurred during OCR processing", exc_info=True)
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/translate_image', methods=['POST'])
def translate_image():
    """Endpoint for image translation with post-processing."""
    if 'image_file' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image_file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        image = Image.open(file.stream).convert("RGB")
        processed_image = preprocess_image(image)
        
        lang = detect_language(processed_image)
        logging.info(f"Using language model: {lang}")

        custom_config = f'-l {lang} --oem 3 --psm 6'
        raw_text = pytesseract.image_to_string(processed_image, config=custom_config)
        
        cleaned_text = post_process_text(raw_text, lang)
        
        return jsonify({'text': cleaned_text})
    except Exception as e:
        logging.error("An error occurred during image translation", exc_info=True)
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    """Extracts text directly from a searchable PDF file."""
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No PDF file provided'}), 400

    file = request.files['pdf_file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        pdf_bytes = file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        full_text = ""
        for page in doc:
            full_text += page.get_text() + "\n"
        doc.close()

        cleaned_text = ' '.join(full_text.split())
        
        return jsonify({'text': cleaned_text})

    except Exception as e:
        logging.error("An error occurred during PDF processing", exc_info=True)
        return jsonify({'error': f'Failed to process PDF: {str(e)}'}), 500
        
@app.route('/translate_image_stream', methods=['POST'])
def translate_image_stream():
    """Handles a single image sent as a raw byte stream with post-processing."""
    try:
        image_bytes = request.get_data()
        if not image_bytes:
            return jsonify(error="No data received in request body"), 400

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        processed_image = preprocess_image(image)
        
        lang = detect_language(processed_image)
        logging.info(f"Using language model: {lang}")
        
        custom_config = f'-l {lang} --oem 3 --psm 6'
        raw_text = pytesseract.image_to_string(processed_image, config=custom_config)
        
        cleaned_text = post_process_text(raw_text, lang)
        
        return jsonify({'text': cleaned_text})
    except Exception as e:
        logging.error("An error occurred during image stream processing", exc_info=True)
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@app.route('/process_pdf_stream', methods=['POST'])
def process_pdf_stream():
    """Handles a PDF file sent as a raw byte stream."""
    try:
        pdf_bytes = request.get_data()
        if not pdf_bytes:
            return jsonify(error="No data received in request body"), 400
        
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        full_text = ""
        for page in doc:
            full_text += page.get_text() + "\n"
        doc.close()

        cleaned_text = ' '.join(full_text.split())
        
        return jsonify({'text': cleaned_text})

    except Exception as e:
        logging.error("An error occurred during PDF stream processing", exc_info=True)
        return jsonify({'error': f'Failed to process PDF: {str(e)}'}), 500

if __name__ == '__main__':
    serve(app, host='127.0.0.1', port=5004, threads=100)