import os
# For OCR, Tesseract is a common choice.
# Requires Tesseract OCR engine to be installed on the system,
# and the pytesseract Python wrapper.
# Add "pytesseract" and "Pillow" to requirements.txt.
try:
    import pytesseract
    from PIL import Image
except ImportError:
    print("pytesseract or Pillow not installed. Image parsing (OCR) will not be available. "
          "Please install them with: pip install pytesseract Pillow "
          "And ensure Tesseract OCR engine is installed on your system.")

class ImageParser:
    def __init__(self, tesseract_cmd: str = None):
        """
        Initializes the ImageParser.

        Args:
            tesseract_cmd (str, optional): Path to the Tesseract executable.
                                           If None, pytesseract will try to find it automatically.
                                           Set this if Tesseract is not in your PATH.
                                           e.g., r'C:\Program Files\Tesseract-OCR\tesseract.exe' on Windows.
        """
        if 'pytesseract' not in globals() or 'Image' not in globals():
            raise ImportError(
                "pytesseract or Pillow is not installed. "
                "Image parsing (OCR) functionality is unavailable. "
                "Install them with 'pip install pytesseract Pillow' "
                "and ensure the Tesseract OCR engine is installed system-wide."
            )

        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        try:
            # Check if Tesseract is accessible
            pytesseract.get_tesseract_version()
        except Exception as e: # Could be FileNotFoundError or TesseractNotFound Error
            raise RuntimeError(
                "Tesseract OCR engine not found or not configured correctly. "
                f"Please ensure it's installed and in your PATH, or set tesseract_cmd. Error: {e}"
            )


    def parse(self, file_path: str, lang: str = 'eng') -> str:
        """
        Parses an image file and extracts text content using OCR.

        Args:
            file_path (str): The path to the image file (e.g., PNG, JPG, TIFF).
            lang (str, optional): The language for OCR. Defaults to 'eng' (English).
                                  Multiple languages can be specified, e.g., 'eng+fra'.

        Returns:
            str: The extracted text content from the image.
                 Returns an error message string if parsing fails.

        Raises:
            FileNotFoundError: If the file_path does not exist.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image file not found: {file_path}")

        try:
            image = Image.open(file_path)
            text_content = pytesseract.image_to_string(image, lang=lang)
            return text_content
        except pytesseract.TesseractError as te:
            # Errors related to Tesseract processing
            print(f"Tesseract OCR error for image '{file_path}': {te}")
            return f"Error: Tesseract OCR failed. Details: {te}"
        except Exception as e:
            # Other errors (e.g., file corruption, Pillow issues)
            print(f"Error parsing image file '{file_path}': {e}")
            return f"Error: Could not parse image file. Details: {e}"

# Example Usage (for testing)
if __name__ == '__main__':
    # This example requires:
    # 1. Tesseract OCR engine installed on your system.
    # 2. pytesseract and Pillow installed in your Python environment.
    # 3. An image file (e.g., 'test_sample_image.png') with some text.

    # Path to your Tesseract installation if not in PATH (example for Windows)
    # TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    TESSERACT_PATH = None # Set this if needed

    try:
        parser = ImageParser(tesseract_cmd=TESSERACT_PATH)

        # Create a dummy image for testing (requires Pillow for this part)
        sample_image_path = "test_sample_ocr_image.png"
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (400, 100), color = (255, 255, 255))
            d = ImageDraw.Draw(img)
            try:
                # Try to use a common font, fallback if not found
                font = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                font = ImageFont.load_default()
            d.text((10,30), "Hello OCR Test 123", fill=(0,0,0), font=font)
            img.save(sample_image_path)
            print(f"Created dummy image: {sample_image_path}")

            print("\n--- Parsing Image File ---")
            # Ensure the image path is correct for your test setup
            if os.path.exists(sample_image_path):
                content = parser.parse(sample_image_path)
                if content.startswith("Error:"):
                    print(content)
                else:
                    print(f"Extracted Text: \"{content.strip()}\"")
            else:
                print(f"Test image '{sample_image_path}' not found. Skipping parse test.")

            # Clean up
            if os.path.exists(sample_image_path):
                os.remove(sample_image_path)
                print(f"\nCleaned up dummy image: {sample_image_path}")

        except ImportError:
            print("Pillow not available to create a test image. Skipping image creation.")
        except Exception as e:
            print(f"Could not run ImageParser example (possibly during test image creation): {e}")

    except (ImportError, RuntimeError) as e:
        # This catches errors from ImageParser.__init__ if Tesseract is not set up
        print(f"ImageParser could not be initialized: {e}")
        print("Skipping ImageParser example. Ensure Tesseract OCR and pytesseract/Pillow are installed and configured.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
