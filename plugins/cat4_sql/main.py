"""
Author: Roberto Moscetti
Forked from: https://github.com/Jhonnyr97/AIChatSQL

This script defines a tool for interacting with a SQL database using natural language.
It utilizes the LangChain library to create a chain of operations that validate, optimize, and execute SQL queries.
The results are returned in plain, human-readable text.

Key functionalities:
- Extract SQL queries from input text using regular expressions.
- Define a tool that connects to a database and processes user input.
- Create a SQL query chain using LangChain.
- Load settings and generate a system prompt for the SQL assistant.
- Validate and execute the SQL query, returning the results.

The code uses metadata about the database schema (such as column names and descriptions) to make the large language model (LLM) more precise in generating SQL queries.
This metadata is included in the system prompt to provide context for the LLM, ensuring more accurate and relevant query generation.

Dependencies:
- langchain_community
- cat.mad_hatter
- sqlalchemy
- re
- subprocess
"""

from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from cat.mad_hatter.decorators import tool, hook
from langchain.chains import create_sql_query_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import subprocess
from sqlalchemy import create_engine, inspect
import re

def extract_query(input_query):
    """
    Extracts the SQL query from the input text using a regular expression.
    The SQL query is expected to be enclosed in triple backticks (```sql ... ```).

    Args:
        input_query (str): The input text containing the SQL query.

    Returns:
        str: The extracted SQL query.
    """
    regex_output = re.search('```sql(.*?)```', input_query, re.DOTALL)
    output_query = regex_output.group(1).strip()
    return output_query

@tool (examples=[
    "$database$", 
    "$DATABASAE$", 
    "DB query", 
    "database interaction", 
    "query the database",  
    "Retrieve info using SQL", 
    "Get data from the database",
    
])
def database(tool_input, cat):
    """
    Tool for interacting with an SQL database via natural language input.
    This tool converts natural language questions into SQL queries using a large language model (LLM).
    The queries are executed on a connected database and the results are returned in human-readable text.

    Args:
        tool_input (str): User's natural language question.
        cat: The context object providing necessary database settings and LLM configurations.

    Returns:
        str: The SQL query result or an error message if the query could not be processed.
    """

    db, column_names, column_comments = connect(cat)
    chain = create_sql_query_chain(cat._llm, db)
    
    # Retrieve settings from the plugin configuration
    settings = cat.mad_hatter.plugins["cat4_sql"].load_settings()

    # Format column metadata for inclusion in the system prompt
    comment_list = '\n'.join([f"- {name}, {comment}" for name, comment in zip(column_names, column_comments)])

    # System prompt to guide the SQL assistant
    system = f"""
    You are a SQL assistant for {settings["data_source"]}.
    Your role is to extract from a database structured as follows:
    1. Database name: {settings["database"]}
    2. Table name: {settings["allowed_tables"]}
    3. Column names and descriptions:
        {comment_list}

    Your answer is a SQL query without any additional text or comments.
    """
    
    # Create a prompt template with the system message and user query
    prompt = ChatPromptTemplate.from_messages(
        [("system", system), ("human", "{query}")]
    ).partial(dialect=db.dialect)

    # Validation chain for SQL query generation
    validation_chain = prompt | cat._llm | StrOutputParser()

    # Combine query chain and validation chain
    full_chain = {"query": chain } | validation_chain

    # Generate the SQL query from the user's input
    query = full_chain.invoke(
        {
            "question": tool_input
        }
    )

    # Debugging: Log the generated query and system prompt
    #with open("/app/cat/plugins/cat4_sql/log_query.txt", "a") as file:
    #    file.write("## SYSTEM:\n" + system + "\n\n")
    #    file.write("##\n" + query + "\n\n")

    # Extract and execute the query if valid SQL is detected
    if "```sql" in query:
        query = extract_query(query)
    
    if "SELECT" in query:
        output = str("This is the used query:\n" + query + "\nThis is the output of the query:\n" + db.run(query) + "\nIf present, remove parenthesis and comma from the output.")
    else:
        output = "You are sorry. You don't know how to extract data from the database."
    return output

@hook(priority=0)
def before_cat_bootstrap(cat) -> None:
    """
    Hook to perform system checks before the CAT tool starts.
    This hook ensures that necessary packages and libraries are installed and configured.

    Args:
        cat: The context object for the CAT tool.
    """
    check_pkg_config()
    check_libmysqlclient()
    check_mysqlclient_module()


def check_pkg_config():
    """
    Checks for the presence of pkg-config and installs it if missing.
    """
    try:
        subprocess.check_call(["pkg-config", "--version"])
    except subprocess.CalledProcessError:
        print("Installing pkg-config")
        subprocess.check_call(["apt-get", "-y", "update"])
        subprocess.check_call(["apt-get", "-y", "install", "pkg-config"])


def check_libmysqlclient():
    """
    Checks for the presence of the default MySQL client library and installs it if missing.
    """
    try:
        subprocess.check_call(["pkg-config", "--exists", "default-libmysqlclient"])
    except subprocess.CalledProcessError:
        print("Installing default-libmysqlclient-dev")
        subprocess.check_call(["apt-get", "-y", "install", "default-libmysqlclient-dev"])


def check_mysqlclient_module():
    """
    Checks for the mysqlclient Python module and installs it if missing.
    """
    try:
        import mysqlclient
    except ImportError:
        print("Installing mysqlclient")
        subprocess.check_call(["pip", "install", "mysqlclient"])


def connect(cat):
    """
    Connects to the specified SQL database based on settings from the CAT context.
    This function creates a connection to the database and retrieves metadata about the allowed tables.

    Args:
        cat: The context object containing plugin settings.

    Returns:
        tuple: A tuple containing the SQL database object, column names, and column comments.
    """
    settings = cat.mad_hatter.plugins["cat4_sql"].load_settings()
    if settings["data_source"] == "sqlite":
        uri = f"sqlite:///cat/plugins/sqlite_db/{settings['host']}"
    elif settings["data_source"] == "postgresql":
        uri = f"postgresql+psycopg2://{settings['username']}:{settings['password']}@{settings['host']}:{settings['port']}/{settings['database']}"
    else:
        uri = f"mysql://{settings['username']}:{settings['password']}@{settings['host']}:{settings['port']}/{settings['database']}"

    db = SQLDatabase.from_uri(uri,
                                    include_tables=settings["allowed_tables"].split(", "),
                                    )

    engine = create_engine(uri)
    
    # Use inspector to retrieve column names and comments
    inspector = inspect(engine)
    table_name = settings["allowed_tables"]
    column_names = [column["name"] for column in inspector.get_columns(table_name)]
    column_comments = [column["comment"] for column in inspector.get_columns(table_name)]
    
    # Debugging: Log column metadata
    #with open("/app/cat/plugins/cat4_sql/columns.txt", "w") as file:
    #    file.write(str(column_names))
    #    file.write(str(column_comments))

    return db, column_names, column_comments