from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import cv2
import numpy as np
import os
import fitz
import logging
from flask_cors import CORS
from werkzeug.serving import run_simple
import io

# --- Basic Setup ---
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
CORS(app, resources={r"/*": {"origins": "*"}})

# --- Tesseract Path Configuration ---
pytesseract.pytesseract.tesseract_cmd = os.path.join(os.path.dirname(__file__), 'tesseract', 'tesseract.exe')

def preprocess_image(image):
    """Converts image to grayscale, applies thresholding, and removes noise."""
    img_np = np.array(image)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return processed_img


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
        
        # Use both English and Arabic language models
        custom_config = r'-l eng+ara'
        text = pytesseract.image_to_string(processed_image, config=custom_config)
        
        # Clean up the extracted text
        cleaned_text = ' '.join(text.split())
        
        return jsonify({'text': cleaned_text})
    except Exception as e:
        logging.error("An error occurred during OCR processing", exc_info=True)
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/translate_image', methods=['POST'])
def translate_image():
    if 'image_file' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image_file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        image = Image.open(file.stream).convert("RGB")
        processed_image = preprocess_image(image)
        
        # Use both English and Arabic language models
        custom_config = r'-l eng+ara'
        text = pytesseract.image_to_string(processed_image, config=custom_config)
        
        # Clean up the extracted text
        cleaned_text = ' '.join(text.split())
        
        return jsonify({'text': cleaned_text})
    except Exception as e:
        logging.error("An error occurred during image translation", exc_info=True)
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    """Extracts text directly from a PDF file."""
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

        # Clean up the extracted text
        cleaned_text = ' '.join(full_text.split())
        
        return jsonify({'text': cleaned_text})

    except Exception as e:
        logging.error("An error occurred during PDF processing", exc_info=True)
        return jsonify({'error': f'Failed to process PDF: {str(e)}'}), 500
        
@app.route('/translate_image_stream', methods=['POST'])
def translate_image_stream():
    """
    Handles a single image sent as a raw byte stream.
    The internal logic mirrors the original /translate_image endpoint.
    """
    try:
        # Read the raw request body into an in-memory buffer
        image_bytes = request.get_data()
        if not image_bytes:
            return jsonify(error="No data received in request body"), 400

        # Use the exact same processing logic as the original endpoint
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        processed_image = preprocess_image(image)
        
        custom_config = r'-l eng+ara'
        text = pytesseract.image_to_string(processed_image, config=custom_config)
        
        cleaned_text = ' '.join(text.split())
        
        return jsonify({'text': cleaned_text})
    except Exception as e:
        logging.error("An error occurred during image stream processing", exc_info=True)
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@app.route('/process_pdf_stream', methods=['POST'])
def process_pdf_stream():
    """
    Handles a PDF file sent as a raw byte stream.
    The internal logic mirrors the original /process_pdf endpoint.
    """
    try:
        # Read the raw request body
        pdf_bytes = request.get_data()
        if not pdf_bytes:
            return jsonify(error="No data received in request body"), 400
        
        # Use the exact same processing logic as the original endpoint
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
    run_simple(
        '127.0.0.1',
        5004,
        app,
        use_reloader=False,
        use_debugger=True,
        threaded=True,
        exclude_patterns=['*__pycache__*', '*venv*', '*uploads*','*tesseract*']
    )