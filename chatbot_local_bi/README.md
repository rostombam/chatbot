# Chatbot Local BI

This application allows you to upload a CSV or Excel file and ask questions about its content using a chatbot interface.

## Prerequisites

- Python 3.7+
- OpenAI API Key

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd chatbot_local_bi
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set your OpenAI API Key:**
   Set the `OPENAI_API_KEY` environment variable. You can do this by:
   - Exporting it in your terminal: `export OPENAI_API_KEY='your_api_key'`
   - Creating a `.env` file in the project root and adding `OPENAI_API_KEY='your_api_key'`

## Usage

1. **Run the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser:**
   Streamlit will typically open the application automatically in your default web browser (usually at `http://localhost:8501`).

3. **Upload your data:**
   - Use the file uploader to select a CSV or Excel file.
   - A preview of the first few rows will be displayed.

4. **Ask questions:**
   - Type your question about the data in the text input field.
   - The chatbot will process your query and display the answer.

## How it works

- **Streamlit:** Used for creating the web interface.
- **Pandas:** Used for data manipulation and reading CSV/Excel files.
- **Langchain:** Used to create an agent that can interact with the pandas DataFrame.
  - `create_pandas_dataframe_agent`: Specifically creates an agent optimized for question answering over DataFrames.
- **OpenAI:** Provides the language model that powers the chatbot's understanding and response generation.

## File Structure

- `app.py`: The main Streamlit application script.
- `requirements.txt`: Lists the Python dependencies for the project.
- `README.md`: This file.
- `example_data/`: (Optional) A directory where you can place sample data files.

## Error Handling

- The application checks if the `OPENAI_API_KEY` is set and displays an error if not.
- It handles potential errors during file upload and data processing.
- Unsupported file types will also trigger an error message.

## Contributing

Contributions are welcome! If you have suggestions for improvements or find any issues, please open an issue or submit a pull request.
