import streamlit as st
from pathlib import Path 
from langchain.agents import create_sql_agent  # construct a SQL agent from an LLM and toolkit or database
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit    # SQL database toolkit 
from sqlalchemy import create_engine    ## sqlalchemy is map output from sql database 
import sqlite3
import mysql.connector
from langchain_groq import ChatGroq
from urllib.parse import quote_plus

st.set_page_config(page_title="Langchain: Chat with SQL DB", page_icon="🦜")
st.title("🦜 Langchain: Chat with SQL DB")

LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

radio_opt=["Use SQLite 3 Database - Student.db", "Connect to you MYSQL Database"]
selected_opt = st.sidebar.radio(label="Choose the DB which you want to chat", options=radio_opt)
###########
# --- Optional: clear cache and rerun ---
if st.sidebar.button("🔄 Clear cache and reload DB"):
    st.cache_resource.clear()
    st.experimental_rerun()

###########

if radio_opt.index(selected_opt)==1:
    db_uri=MYSQL
    mysql_host = st.sidebar.text_input("Provide MySQL Host")
    mysql_user = st.sidebar.text_input("MYSQL User")
    mysql_password = st.sidebar.text_input("MYSQl password", type="password")
    mysql_db=st.sidebar.text_input("MYSQL database")
    
else: 
    db_uri=LOCALDB

api_key = st.sidebar.text_input(label= "Groq API key" , type= "password")

if not db_uri:
    st.info("Please enter the database information and uri")

if not api_key:
    st.info("Please add the groq api key")   

# LLM MODEL 

llm= ChatGroq(groq_api_key=api_key,model_name="Llama3-8b-8192",streaming=True)

# @st.cache_resource(ttl="2h")
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    if db_uri==LOCALDB:
        dbfilepath=(Path(__file__).parent/"student.db").absolute()
        print("Connecting to SQLite DB:", dbfilepath)
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro",uri=True)
        return SQLDatabase(create_engine("sqlite://", creator=creator))
    elif db_uri == MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL connection details.")
            st.stop()

    #  URL encode password to avoid special character errors
    encoded_password = quote_plus(mysql_password)

    return SQLDatabase(
        create_engine(
            f"mysql+mysqlconnector://{mysql_user}:{encoded_password}@{mysql_host}/{mysql_db}"
        )
    )

    
if db_uri==MYSQL:
    db=configure_db(db_uri,mysql_host, mysql_user , mysql_password,mysql_db)
else:
    db=configure_db(db_uri)    

# toolkit 
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors= True
)

if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state['messages'] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


user_query= st.chat_input(placeholder="Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role":"user","content":user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback=StreamlitCallbackHandler(st.container())
        response = agent.run(user_query,callbacks=[streamlit_callback])
        st.session_state.messages.append({"role":"assistant","content":response})
        st.write(response)
    