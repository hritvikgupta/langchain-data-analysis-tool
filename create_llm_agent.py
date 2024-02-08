import pandas as pd
import numpy as np
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_community.llms import OpenAI
import os
import openai
from langchain.agents import AgentType, initialize_agent
from langchain_community.tools import E2BDataAnalysisTool
from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()
from e2b import Sandbox

# sandbox.close()

os.environ['PYTHONHTTPSVERIFY'] = '0'  # WARNING: Use as a last resort only

E2B_API_KEY = os.environ["E2B_API_KEY"] 
OPEN_AI_API_KEY = os.environ["OPENAI_API_KEY"]
# sandbox = Sandbox(api_key=E2B_API_KEY)

# df = pd.read_csv('/Users/hritvikgupta/Downloads/Langchain-DataAnalysis-Tool/uploads/titanic_dataset.csv')

def save_artifact(artifact):
  print("New matplotlib chart generated", artifact.name)
  file = artifact.download()
  basename = os.path.basename(artifact.name)
  with open(f"./charts/{basename}", "wb") as f:
        f.write(file)

def llm_agent(dataset_path, description):
    e2b_data_analysis_tool = E2BDataAnalysisTool(
        # Pass environment variables to the sandbox
        env_vars={"OPEN_AI_API_KEY": OPEN_AI_API_KEY,"E2B_API_KEY":E2B_API_KEY },
        on_stdout=lambda stdout: print("stdout:", stdout),
        on_stderr=lambda stderr: print("stderr:", stderr),
        on_artifact=save_artifact,
    )

    csv_file_path = dataset_path
    with open(csv_file_path) as f:
        remote_path = e2b_data_analysis_tool.upload_file(
            file=f,
            description=description,
        )
        print(remote_path)

    e2b_data_analysis_tool.install_python_packages("pandas")
    e2b_data_analysis_tool.install_python_packages("matplotlib")
    e2b_data_analysis_tool.install_python_packages("numpy")

    tools = [e2b_data_analysis_tool.as_tool()]

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True,
        handle_parsing_errors=True,
    )

    return agent

