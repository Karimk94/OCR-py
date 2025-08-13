import platform
import subprocess

def check_tesseract_installation():
    """Checks if Tesseract is installed and accessible in the system's PATH."""
    try:
        subprocess.run(["tesseract", "--version"], check=True, capture_output=True)
        print("Tesseract installation found.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    """
    Guides the user through the Tesseract setup process.
    Tesseract is a system application, not a Python package, so it must be installed manually.
    """
    print("--- Tesseract OCR Setup Guide ---")
    print("This API requires the Tesseract OCR engine to be installed on your system.")

    if check_tesseract_installation():
        print("\nSetup check complete. Tesseract is ready to use.")
        return

    print("\n[ACTION REQUIRED] Please install Tesseract OCR manually.")
    
    system = platform.system()
    if system == "Windows":
        print("\n1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Run the installer. During installation, make sure to select the option to add Tesseract to your system PATH.")
        print("3. After installation, re-run this setup script ('setup.bat') to verify.")
    elif system == "Darwin": # macOS
        print("\n1. Open your terminal.")
        print("2. If you don't have Homebrew, install it from: https://brew.sh")
        print("3. Run the command: brew install tesseract")
        print("4. After installation, re-run this setup script.")
    elif system == "Linux":
        print("\n1. Open your terminal.")
        print("2. Run the command for your distribution:")
        print("   - Debian/Ubuntu: sudo apt update && sudo apt install tesseract-ocr")
        print("   - Fedora: sudo dnf install tesseract")
        print("3. After installation, re-run this setup script.")
    else:
        print(f"\nUnsupported operating system: {system}. Please find Tesseract installation instructions for your OS online.")

    print("\nThis script does not download any models itself; it only checks for the Tesseract application.")

if __name__ == "__main__":
    main()
