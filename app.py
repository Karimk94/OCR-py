from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import cv2
import numpy as np
import os
import fitz

# --- Tesseract Path Configuration ---
# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = os.path.join(os.path.dirname(__file__), 'tesseract', 'tesseract.exe')
tessdata_dir_config = f'--tessdata-dir "{os.path.join(os.path.dirname(__file__), "tesseract", "tessdata")}"'

app = Flask(__name__)

def preprocess_image(image):
    """Converts image to grayscale, applies thresholding, and removes noise."""
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    # Apply adaptive thresholding for better results on varied lighting
    processed_img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return processed_img

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
        custom_config = r'-l eng+ara ' + tessdata_dir_config
        text = pytesseract.image_to_string(processed_image, config=custom_config)
        
        # Clean up the extracted text
        cleaned_text = ' '.join(text.split())
        
        return jsonify({'text': cleaned_text})
    except Exception as e:
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
        return jsonify({'error': f'Failed to process PDF: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
