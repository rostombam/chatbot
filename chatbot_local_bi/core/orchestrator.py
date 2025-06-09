import os
import pandas as pd
from langchain_openai import OpenAI, ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent

# from .nlp.intent_classifier import IntentClassifier # Assuming future use
# from .data_extractor import pdf_parser, excel_parser, docx_parser, image_parser # Assuming future use
# from .bi_analyzer.analyzer import BIAnalyzer # Assuming future use
# from .report_generator.generator import ReportGenerator # Assuming future use

class ChatbotOrchestrator:
    def __init__(self, openai_api_key: str, model_name: str = "gpt-3.5-turbo"):
        """
        Initializes the orchestrator with an OpenAI API key and a model name.

        Args:
            openai_api_key (str): The API key for OpenAI services.
            model_name (str, optional): The model name to use for LLM interactions.
                                        Defaults to "gpt-3.5-turbo".
        """
        if not openai_api_key:
            raise ValueError("OpenAI API key must be provided.")

        self.openai_api_key = openai_api_key
        self.llm = OpenAI(api_key=self.openai_api_key, temperature=0) # For general tasks, perhaps summarization
        self.chat_llm = ChatOpenAI(api_key=self.openai_api_key, model_name=model_name, temperature=0) # For conversational tasks

        # Placeholder for intent classifier, data extractors, etc.
        # self.intent_classifier = IntentClassifier(self.chat_llm)
        # self.pdf_parser = pdf_parser.PDFParser()
        # self.excel_parser = excel_parser.ExcelParser()
        # self.docx_parser = docx_parser.DocxParser()
        # self.image_parser = image_parser.ImageParser() # Requires additional setup for OCR
        # self.bi_analyzer = BIAnalyzer(self.chat_llm)
        # self.report_generator = ReportGenerator(self.llm)

        self.dataframe = None
        self.df_agent = None
        self.df_id = None

    def load_data(self, file_path: str, file_type: str = None) -> str:
        """
        Loads data from a given file path into a pandas DataFrame.
        The file type is inferred if not provided.

        Args:
            file_path (str): The path to the data file.
            file_type (str, optional): The type of the file (e.g., 'csv', 'xlsx').
                                       Defaults to None, in which case it's inferred.

        Returns:
            str: A message indicating the result of the data loading operation.

        Raises:
            FileNotFoundError: If the file_path does not exist.
            ValueError: If the file type is unsupported or cannot be inferred.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_type is None:
            _, extension = os.path.splitext(file_path)
            file_type = extension.lower().strip('.')

        try:
            if file_type == 'csv':
                self.dataframe = pd.read_csv(file_path)
            elif file_type in ['xls', 'xlsx']:
                self.dataframe = pd.read_excel(file_path)
            # elif file_type == 'pdf':
            #     text_content = self.pdf_parser.parse(file_path)
            #     # Further processing needed to convert PDF text to structured DataFrame
            #     # This is a placeholder and would require significant implementation.
            #     self.dataframe = pd.DataFrame([{"pdf_content": text_content}]) # Example
            # elif file_type == 'docx':
            #     text_content = self.docx_parser.parse(file_path)
            #     self.dataframe = pd.DataFrame([{"docx_content": text_content}]) # Example
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

            self.df_id = os.path.basename(file_path)
            # Initialize the agent after loading data
            self._create_agent()
            return f"Data from '{self.df_id}' loaded successfully. Columns: {self.dataframe.columns.tolist()}"

        except Exception as e:
            self.dataframe = None
            self.df_agent = None
            self.df_id = None
            return f"Error loading data: {str(e)}"

    def _create_agent(self):
        """
        Creates or recreates the pandas DataFrame agent if a DataFrame is loaded.
        """
        if self.dataframe is not None:
            self.df_agent = create_pandas_dataframe_agent(
                self.chat_llm,
                self.dataframe,
                verbose=True,
                agent_executor_kwargs={"handle_parsing_errors": True} # Handles errors in LLM output parsing
            )
        else:
            self.df_agent = None

    def get_dataframe_head(self, n: int = 5) -> (str | None):
        """
        Returns the first n rows of the loaded DataFrame as an HTML string.

        Args:
            n (int): Number of rows to display.

        Returns:
            str | None: HTML string of the DataFrame head, or None if no data is loaded.
        """
        if self.dataframe is not None:
            return self.dataframe.head(n).to_html()
        return None

    def process_query(self, query: str) -> str:
        """
        Processes a user query using the pandas DataFrame agent.

        Args:
            query (str): The user's question about the data.

        Returns:
            str: The agent's response to the query.
        """
        if self.df_agent is None:
            return "No data loaded. Please upload a file first."

        if not query:
            return "Query cannot be empty."

        try:
            # Pre-processing or intent classification could happen here
            # intent = self.intent_classifier.classify(query)
            # if intent == "data_query":
            response = self.df_agent.run(query)
            # elif intent == "report_generation":
            #    analysis = self.bi_analyzer.analyze(self.dataframe, query) # Simplified
            #    response = self.report_generator.generate(analysis)
            # else:
            #    response = "I'm not sure how to handle that query."
            return str(response)
        except Exception as e:
            # Log the full error for debugging
            print(f"Error during agent query processing: {e}")
            return f"Error processing query: {str(e)}. Try rephrasing your question."

    def get_df_id(self) -> (str | None):
        """Returns the ID of the currently loaded DataFrame."""
        return self.df_id

# Example Usage (for testing purposes, not part of the Flask app flow directly)
if __name__ == '__main__':
    # This requires OPENAI_API_KEY to be set in the environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set the OPENAI_API_KEY environment variable to run this example.")
    else:
        orchestrator = ChatbotOrchestrator(openai_api_key=api_key)

        # Create a dummy CSV for testing
        dummy_data = {'col1': [1, 2, 3], 'col2': ['a', 'b', 'c'], 'sales': [100, 200, 150]}
        dummy_df = pd.DataFrame(dummy_data)
        dummy_csv_path = "dummy_data.csv"
        dummy_df.to_csv(dummy_csv_path, index=False)

        print(orchestrator.load_data(dummy_csv_path))

        if orchestrator.get_dataframe_head():
            print("\nData Head:")
            # In a real scenario, this HTML would be rendered. Here we just print it.
            # For testing, we might want to parse it or just confirm it's not None.
            print(orchestrator.get_dataframe_head())

        print("\nQuerying data...")
        response = orchestrator.process_query("What is the total sales?")
        print(f"Response: {response}")

        response_col_sum = orchestrator.process_query("What is the sum of col1?")
        print(f"Response for sum of col1: {response_col_sum}")

        # Clean up dummy file
        os.remove(dummy_csv_path)
