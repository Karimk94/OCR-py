# Local OCR API with Tesseract

This project provides a robust, Flask-based API for performing high-quality **Optical Character Recognition (OCR)**. It is designed to run **completely offline** and uses the powerful and widely-trusted **Tesseract OCR engine**.

This version is the most reliable solution for extracting text from images with complex layouts, such as paragraphs, titles, and varied fonts.

## Features

* **Accurate Full-Page OCR:** Utilizes Tesseract, the industry-standard open-source OCR engine, for excellent performance on full-page documents.
* **100% Offline:** After a one-time setup of Tesseract, the entire application works without any internet connection. It has no dependency on cloud services or external model servers like Ollama.
* **Simple & Reliable API:** Provides a single, stable API endpoint (`/translate_image`) for easy integration into other systems, like your EDMS crawler.
* **Minimal Dependencies:** Requires only a few common Python libraries and a system-level installation of Tesseract.

## How It Works

1.  **System-Level Setup:** Tesseract OCR must be installed on the machine running the API. This is a one-time setup.
2.  **API Call:** An external application sends a `POST` request to the `/translate_image` endpoint with an image file.
3.  **Backend Processing:** The Flask server receives the image and uses the `pytesseract` Python library to interface with the installed Tesseract engine.
4.  **Local OCR:** The Tesseract engine processes the image locally and returns all the text it finds.
5.  **JSON Response:** The Flask server sends the extracted text back to the calling application in a clean JSON format.

## Project Structure



/local-ocr-api
|
|-- app.py # Main Flask application with the API endpoint
|-- requirements.txt # Python dependencies
|-- download_models.py # A helper script to guide Tesseract installation
|-- setup.bat # Windows script to automate the setup process
|-- run.bat # Windows script to run the API server
|-- uploads/ # Temporary folder for images (auto-created)
|-- README.md
## Setup and Installation

### Prerequisites

* Python 3.7+
* Administrator/sudo rights to install system-level software (Tesseract).

### Installation Steps (Windows)

The provided scripts make setup on Windows straightforward.

1.  **Run `setup.bat` as Administrator**
    Right-click `setup.bat` and choose "Run as administrator". The script will:
    * Create a Python virtual environment.
    * Install the required Python packages (`Flask`, `Pillow`, `pytesseract`).
    * Run a helper script that will check for Tesseract and guide you to install it if it's missing.

2.  **Install Tesseract OCR**
    If the setup script tells you Tesseract is not found, follow these steps:
    * Go to [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki) and download the recommended installer.
    * Run the installer. **Crucially, ensure you select the option to "Add Tesseract to system PATH"**.
    * After the installation is complete, you can run `setup.bat` again to confirm it's detected.

3.  **Run the API**
    Once setup is complete, simply double-click `run.bat` to start the server.

### Manual Setup (macOS / Linux)

1.  **Install Tesseract:**
    * **macOS:** `brew install tesseract`
    * **Debian/Ubuntu:** `sudo apt update && sudo apt install tesseract-ocr`

2.  **Install Python Dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3.  **Run the API:**
    ```bash
    python app.py
    ```
The API will now be running and accessible at `http://<your-machine-ip>:5002`.


