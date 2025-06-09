import os
# For PDF parsing, PyMuPDF (fitz) is efficient and commonly used.
# You'll need to add "PyMuPDF" to your requirements.txt
try:
    import fitz  # PyMuPDF
except ImportError:
    # This message is for developers; users will see errors if PyMuPDF is not installed
    # and this module is used.
    print("PyMuPDF not installed. PDF parsing will not be available. "
          "Please install it with: pip install PyMuPDF")

class PDFParser:
    def __init__(self):
        """
        Initializes the PDFParser.
        Checks if the required library (PyMuPDF) is available.
        """
        if 'fitz' not in globals():
            raise ImportError(
                "PyMuPDF (fitz) is not installed. "
                "PDF parsing functionality is unavailable. "
                "Install it with 'pip install PyMuPDF'."
            )

    def parse(self, file_path: str) -> str:
        """
        Parses a PDF file and extracts all text content.

        Args:
            file_path (str): The path to the PDF file.

        Returns:
            str: The extracted text content from the PDF.
                 Returns an error message string if parsing fails.

        Raises:
            FileNotFoundError: If the file_path does not exist.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            doc = fitz.open(file_path)
            text_content = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_content.append(page.get_text("text"))

            doc.close()
            return "\n".join(text_content)
        except Exception as e:
            # Log the error or handle it more gracefully
            print(f"Error parsing PDF file '{file_path}': {e}")
            return f"Error: Could not parse PDF file. Details: {e}"

    def parse_to_pages(self, file_path: str) -> list[str]:
        """
        Parses a PDF file and extracts text content page by page.

        Args:
            file_path (str): The path to the PDF file.

        Returns:
            list[str]: A list where each element is the text content of a page.
                       Returns an empty list if parsing fails or the PDF is empty.

        Raises:
            FileNotFoundError: If the file_path does not exist.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        pages_text = []
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pages_text.append(page.get_text("text"))
            doc.close()
        except Exception as e:
            print(f"Error parsing PDF file '{file_path}' to pages: {e}")
            # Optionally, return a list with a single error string or raise
            # For now, returning empty list on error to match "empty PDF" case.
            return []
        return pages_text

# Example Usage (for testing)
if __name__ == '__main__':
    # This example assumes you have a PDF file named 'sample.pdf' in the same directory
    # or provide a full path to a test PDF.
    # You would need to create a dummy PDF for this test to run successfully.

    parser = PDFParser()
    sample_pdf_path = "test_sample.pdf" # Replace with a path to an actual PDF file

    # Create a dummy PDF for testing if PyMuPDF is available
    if 'fitz' in globals():
        try:
            doc = fitz.open() # New empty PDF
            page = doc.new_page()
            page.insert_text((50, 72), "Hello, this is a test PDF content on page 1.")
            page = doc.new_page()
            page.insert_text((50, 72), "This is page 2 of the test PDF.")
            doc.save(sample_pdf_path)
            doc.close()

            print(f"Created dummy PDF: {sample_pdf_path}")

            print("\n--- Parsing entire PDF ---")
            content = parser.parse(sample_pdf_path)
            if content.startswith("Error:"):
                print(content)
            else:
                print(f"Extracted Content (first 100 chars): {content[:100]}...")

            print("\n--- Parsing PDF page by page ---")
            pages = parser.parse_to_pages(sample_pdf_path)
            if not pages:
                print("No pages extracted or error occurred.")
            else:
                for i, page_text in enumerate(pages):
                    print(f"Page {i+1} (first 50 chars): {page_text[:50]}...")

            # Clean up the dummy PDF
            if os.path.exists(sample_pdf_path):
                os.remove(sample_pdf_path)
                print(f"\nCleaned up dummy PDF: {sample_pdf_path}")

        except Exception as e:
            print(f"Could not run PDFParser example: {e}")
            print("Ensure PyMuPDF is installed and you have rights to create files here.")
    else:
        print("PyMuPDF (fitz) is not installed. Skipping PDFParser example.")
