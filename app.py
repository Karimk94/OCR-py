import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract

# --- Configuration ---
pytesseract.pytesseract.tesseract_cmd = r'.\tesseract\tesseract.exe'

# Initialize the Flask application
app = Flask(__name__)

# Configure a folder for temporary uploads
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

def allowed_file(filename):
    """Checks if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/translate_image', methods=['POST'])
def translate_image():
    """
    API endpoint that receives an image file, extracts text using local Tesseract OCR,
    and returns the extracted text.
    """
    if 'image_file' not in request.files:
        return jsonify({'error': 'No image file provided.'}), 400

    file = request.files['image_file']

    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid or no selected file.'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        extracted_text = pytesseract.image_to_string(Image.open(filepath), lang='eng+ara')

        return jsonify({'text': extracted_text.strip()})

    except pytesseract.TesseractNotFoundError:
        error_msg = (
            "Tesseract is not installed or not in your system's PATH. "
            "Please install Tesseract OCR (a system-level application) and "
            "ensure its location is in the PATH or set explicitly in app.py."
        )
        print(f"ERROR: {error_msg}")
        return jsonify({'error': error_msg}), 500
    except Exception as e:
        error_msg = "An error occurred during Tesseract OCR processing."
        print(f"ERROR: {error_msg}\nDetails: {e}")
        return jsonify({'error': error_msg, 'details': str(e)}), 500
    finally:
        # Clean up by removing the uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == '__main__':
    # Running on 0.0.0.0 makes the API accessible from other machines
    app.run(host='0.0.0.0', port=5004, debug=False)
