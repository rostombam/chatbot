import os
from flask import Flask, request, jsonify, render_template
import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration
app.config.from_object('config.Config')

# Initialize OpenAI LLM
llm = OpenAI(api_key=app.config["OPENAI_API_KEY"])

# In-memory storage for DataFrame (for simplicity)
# In a production app, you might use a database or a more persistent storage solution
dataframes = {}

@app.route('/', methods=['GET'])
def index():
    """Render the main page with file uploader."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and store DataFrame."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        try:
            filename = file.filename
            if filename.endswith('.csv'):
                df = pd.read_csv(file)
            elif filename.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file)
            else:
                return jsonify({"error": "Unsupported file type. Please upload CSV or Excel."}), 400

            # Store dataframe in memory with a simple ID (e.g., filename)
            # For concurrent users, you'd need a more robust way to manage sessions/data
            df_id = filename
            dataframes[df_id] = df

            return jsonify({
                "message": f"File '{filename}' uploaded successfully.",
                "df_id": df_id,
                "columns": df.columns.tolist(),
                "head": df.head().to_html()
            }), 200
        except Exception as e:
            return jsonify({"error": f"Error processing file: {str(e)}"}), 500

@app.route('/query', methods=['POST'])
def query_data():
    """Handle user queries against an uploaded DataFrame."""
    data = request.get_json()
    if not data or 'df_id' not in data or 'query' not in data:
        return jsonify({"error": "Missing df_id or query in request"}), 400

    df_id = data['df_id']
    user_query = data['query']

    if df_id not in dataframes:
        return jsonify({"error": f"DataFrame with ID '{df_id}' not found. Please upload again."}), 404

    df = dataframes[df_id]

    try:
        # Create pandas dataframe agent
        # Note: It's re-created on each query. For optimization, consider caching agents if llm and df are unchanged.
        agent = create_pandas_dataframe_agent(llm, df, verbose=True)

        # Run the agent with the query
        response = agent.run(user_query)

        return jsonify({"response": response}), 200
    except Exception as e:
        return jsonify({"error": f"Error processing query: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=app.config['DEBUG'])
