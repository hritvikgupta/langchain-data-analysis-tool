import pandas as pd
import numpy as np
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_community.llms import OpenAI
import os
from datetime import datetime
import openai
from langchain.agents import AgentType, initialize_agent
from langchain_community.tools import E2BDataAnalysisTool
from langchain_community.chat_models import ChatOpenAI
from create_llm_agent import llm_agent
from dotenv import load_dotenv
import re
import tempfile

load_dotenv()

os.environ['PYTHONHTTPSVERIFY'] = '0'  # WARNING: Use as a last resort only
    
class EDA():
  def __init__(self, dataset_name, dataset_path, save_code_path, description, images_dir):
    self.dataset_name = dataset_name
    self.dataset_path = dataset_path
    self.save_code_path = save_code_path
    self.description = description
    self.agent = llm_agent(self.dataset_path, self.description)
    self.images_dir = images_dir


  def missing_stat(self, df):
    total = df.isna().sum().sort_values(ascending = False)
    percent = (df.isna().sum() / df.isna().count()).sort_values(ascending=False)
    missing_data = pd.concat([total, percent], axis = 1, keys = ["Total", "Percent"])
    return missing_data

  def imputation(self, df, columns):
    for column in columns:
        # Check if the column is numeric (int64, float64) or categorical/object
        if df[column].dtype in ['int64', 'float64']:
            df[column] = df[column].fillna(df[column].mean())
        else:  # For categorical data, use mode to fill missing values
            df[column] = df[column].fillna(df[column].mode()[0])
    return df

  def handle_missing_values(self, df):
      null_values_sum = df.isna().sum()
      columns_with_null = null_values_sum[null_values_sum > 0].index.tolist()
      updated_df = self.imputation(df, columns_with_null)  # Use self to reference the method within the class
      return updated_df

  def generate_response(self, input):
      prompt = "provide code to first lowercase columns and then" +  input + "and provide code snippet to save it into working directory"
      response = self.agent.run(prompt)
      return response

  def extract_code_from_text(self, text):
    """
    This function extracts and returns the Python code block from a given text.
    
    Args:
    - text (str): The text containing the Python code block enclosed in triple backticks.
    
    Returns:
    - str: The extracted Python code. If no code block is found, returns an empty string.
    """
    # Look for the start and end of the Python code block
    start_marker = "```python"
    end_marker = "```"
    start_index = text.find(start_marker)
    end_index = text.find(end_marker, start_index + len(start_marker))
    
    # Extract and return the code block if found
    if start_index != -1 and end_index != -1:
        return text[start_index + len(start_marker):end_index].strip()
    else:
        return ""

  def extract_and_save(self, response, name, custom_csv_path = None):
        code = self.extract_code_from_text(response)
        code = code.replace("plt.show()", "")

        old_path = '/home/user/' + self.dataset_name
        new_path = self.dataset_path
        
        modified_code = code.replace(old_path, new_path)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_csv_name = f"csv_{timestamp}.csv"
        unique_image_name = f"image_{timestamp}.png"
        if custom_csv_path:
            new_csv_path = os.path.join(self.images_dir, unique_csv_name)
            to_csv_pattern = r"\.to_csv\(\s*['\"](.*?)['\"]\s*,"
            to_csv_replacement = f".to_csv('{new_csv_path}',"
            new_code = re.sub(to_csv_pattern, to_csv_replacement, modified_code)
        else:  
            # Generate a unique filename for the image using a timestamp
            new_image_path = os.path.join(self.images_dir, unique_image_name)
            # Pattern to find matplotlib savefig calls
            pattern = r"plt\.savefig\(\s*['\"](.*?)['\"]\s*\)"
            # Replacement string with the new, dynamically generated image path
            replacement = f"plt.savefig('{new_image_path}')"
            # Replace all occurrences of plt.savefig in the code
            new_code = re.sub(pattern, replacement, modified_code)
        
        # Save the modified code to a file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as tmpfile:
            tmpfile.write(new_code)
            tmp_filename = tmpfile.name
        tmpfile.close()
        return tmp_filename, unique_image_name, unique_csv_name

# dataset_name = "titanic_dataset.csv"
# dataset_path = '/content/titanic_dataset.csv'
# save_code_path = "/content/code.py"


# obj = EDA(dataset_name, dataset_path, save_code_path)
