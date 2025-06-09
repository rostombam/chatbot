import os
import pandas as pd
# pandas itself handles Excel files using engines like openpyxl (for .xlsx) or xlrd (for older .xls).
# Ensure "pandas" and "openpyxl" (or "xlrd") are in requirements.txt.

class ExcelParser:
    def __init__(self):
        """
        Initializes the ExcelParser.
        Pandas will raise ImportError if the necessary engine (e.g., openpyxl) is missing.
        """
        pass # No specific initialization needed beyond pandas installation

    def parse_sheet_to_dataframe(self, file_path: str, sheet_name: str | int = 0, **kwargs) -> (pd.DataFrame | str):
        """
        Parses a specific sheet from an Excel file into a pandas DataFrame.

        Args:
            file_path (str): The path to the Excel file (.xls or .xlsx).
            sheet_name (str | int, optional): The name or index of the sheet to parse.
                                              Defaults to 0 (the first sheet).
            **kwargs: Additional keyword arguments to pass to pandas.read_excel().
                      Example: header=0, skiprows=None, etc.

        Returns:
            pd.DataFrame | str: A pandas DataFrame containing the sheet data,
                                 or an error message string if parsing fails.

        Raises:
            FileNotFoundError: If the file_path does not exist.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel file not found: {file_path}")

        try:
            # pd.read_excel can infer the engine (openpyxl for xlsx, xlrd for xls)
            # If a specific engine is required, it can be passed via kwargs: engine='openpyxl'
            df = pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
            return df
        except ImportError as ie:
            # This typically means the Excel engine (e.g., openpyxl) is not installed.
            print(f"ImportError during Excel parsing: {ie}. Ensure pandas Excel engines are installed.")
            return (f"Error: Missing pandas dependency for Excel. "
                    f"Try: pip install openpyxl xlrd. Details: {ie}")
        except FileNotFoundError: # Should be caught by the initial check, but as a safeguard.
            raise
        except Exception as e:
            # Catches other pandas errors (e.g., sheet not found, corrupted file)
            print(f"Error parsing Excel file '{file_path}', sheet '{sheet_name}': {e}")
            return f"Error: Could not parse Excel sheet. Details: {e}"

    def parse_all_sheets_to_dataframes(self, file_path: str, **kwargs) -> (dict[str, pd.DataFrame] | str):
        """
        Parses all sheets from an Excel file into a dictionary of pandas DataFrames.

        Args:
            file_path (str): The path to the Excel file (.xls or .xlsx).
            **kwargs: Additional keyword arguments to pass to pandas.read_excel().

        Returns:
            dict[str, pd.DataFrame] | str: A dictionary where keys are sheet names
                                           and values are DataFrames.
                                           Returns an error message string if parsing fails.

        Raises:
            FileNotFoundError: If the file_path does not exist.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel file not found: {file_path}")

        try:
            # Setting sheet_name=None tells pandas to read all sheets
            excel_file = pd.ExcelFile(file_path, engine=kwargs.pop('engine', None))
            sheet_names = excel_file.sheet_names

            dataframes = {}
            for sheet_name in sheet_names:
                # Pass along any other kwargs like header, skiprows to the read_excel call for each sheet
                df = excel_file.parse(sheet_name, **kwargs)
                dataframes[sheet_name] = df
            return dataframes
        except ImportError as ie:
            print(f"ImportError during Excel parsing: {ie}. Ensure pandas Excel engines are installed.")
            return (f"Error: Missing pandas dependency for Excel. "
                    f"Try: pip install openpyxl xlrd. Details: {ie}")
        except FileNotFoundError: # Safeguard
            raise
        except Exception as e:
            print(f"Error parsing all sheets from Excel file '{file_path}': {e}")
            return f"Error: Could not parse all Excel sheets. Details: {e}"

# Example Usage (for testing)
if __name__ == '__main__':
    parser = ExcelParser()
    sample_excel_path = "test_sample.xlsx" # Replace with path to an actual Excel file

    # Create a dummy Excel file for testing (requires pandas and openpyxl)
    try:
        # Sample DataFrames
        data1 = {'col1': [1, 2], 'col2': [3, 4]}
        df1 = pd.DataFrame(data1)

        data2 = {'X': ['A', 'B'], 'Y': ['C', 'D'], 'Z': [10.1, 20.2]}
        df2 = pd.DataFrame(data2)

        with pd.ExcelWriter(sample_excel_path, engine='openpyxl') as writer:
            df1.to_excel(writer, sheet_name='Sheet1', index=False)
            df2.to_excel(writer, sheet_name='MyDataSheet', index=False)

        print(f"Created dummy Excel file: {sample_excel_path}")

        print("\n--- Parsing a single sheet (Sheet1) ---")
        result_df1 = parser.parse_sheet_to_dataframe(sample_excel_path, sheet_name='Sheet1')
        if isinstance(result_df1, pd.DataFrame):
            print("DataFrame from Sheet1:")
            print(result_df1.head())
        else:
            print(result_df1) # Print error message

        print("\n--- Parsing a single sheet by index (second sheet) ---")
        result_df_idx = parser.parse_sheet_to_dataframe(sample_excel_path, sheet_name=1) # 0-indexed
        if isinstance(result_df_idx, pd.DataFrame):
            print("DataFrame from second sheet (MyDataSheet):")
            print(result_df_idx.head())
        else:
            print(result_df_idx)


        print("\n--- Parsing all sheets ---")
        all_sheets_result = parser.parse_all_sheets_to_dataframes(sample_excel_path)
        if isinstance(all_sheets_result, dict):
            for sheet_name, df_content in all_sheets_result.items():
                print(f"\nSheet Name: {sheet_name}")
                print(df_content.head())
        else:
            print(all_sheets_result) # Print error message

        # Test non-existent file
        print("\n--- Parsing non-existent file ---")
        try:
            parser.parse_sheet_to_dataframe("non_existent_file.xlsx")
        except FileNotFoundError as e:
            print(f"Caught expected error: {e}")

        # Clean up the dummy Excel file
        if os.path.exists(sample_excel_path):
            os.remove(sample_excel_path)
            print(f"\nCleaned up dummy Excel file: {sample_excel_path}")

    except ImportError:
        print("Pandas or openpyxl not available. Skipping ExcelParser example.")
        print("Install them with: pip install pandas openpyxl")
    except Exception as e:
        print(f"Could not run ExcelParser example: {e}")
        if os.path.exists(sample_excel_path): # Attempt cleanup even on other errors
             os.remove(sample_excel_path)
