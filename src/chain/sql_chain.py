# src/chain/sql_chain.py
import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

load_dotenv()

def build_sql_chain(db_path: str, verbose: bool = False):
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0.7
    )
    db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
    return create_sql_agent(
        llm=llm,
        db=db,
        verbose=verbose,
        agent_type="tool-calling"
    )
