# import streamlit as st

# from intent_classifier import IntentClassifier

# from intent_logger import IntentLogger
# from dotenv import load_dotenv

# # from  ..sql_server import SQLServerConnection
# # from sql_server import SQLServerConnection  # Adjust import path as needed
# # from ..Experiment1.sql_server import SQLServerConnection

# from sql_server import SQLServerConnection


# # Load environment variables
# load_dotenv()

# # Initialize components
# if "db" not in st.session_state:
#     st.session_state.db = SQLServerConnection()
#     st.session_state.connected = st.session_state.db.connect()
# if "intent_classifier" not in st.session_state:
#     st.session_state.intent_classifier = IntentClassifier()
# if "intent_logger" not in st.session_state:
#     st.session_state.intent_logger = IntentLogger(log_file="intent_log.txt")


# # Main UI
# st.title("💬 ChatDB: Run SQL Queries on Your Database")
# st.markdown(
#     "Enter a natural language prompt to classify intent, then provide a SQL query to execute."
# )

# if not st.session_state.connected:
#     st.error("Failed to connect to SQL Server. Check logs for details.")
#     st.stop()

# # Natural language prompt for intent classification
# user_prompt = st.text_input(
#     "Describe what you want (e.g., 'show sales data', 'plot revenue', 'create table'):",
#     placeholder="Example: Show sales data for 2024",
#     key="user_prompt_input",
# )

# # Classify intent if a prompt is provided
# if user_prompt:
#     intent = st.session_state.intent_classifier.classify_intent(user_prompt)
#     st.session_state.intent_logger.log_prompt(user_prompt)
#     st.session_state.intent_logger.log_intent(intent)
#     st.write(f"Classified Intent: **{intent}**")

# # Fetch available tables for the dropdown
# tables = st.session_state.db.get_table_schemas()
# selected_table = st.selectbox("Select a table to query (optional):", [""] + tables)

# # User input: SQL Query
# user_query = st.text_area(
#     "Enter your SQL Query:",
#     placeholder=f"Example: SELECT * FROM {selected_table if selected_table else 'your_table'} LIMIT 5",
#     height=150,
#     key="sql_query_input",
# )

# # Layout for buttons
# col1, col2 = st.columns(2)
# with col1:
#     execute_button = st.button("Execute Query", use_container_width=True)
# with col2:
#     clear_button = st.button("Clear Input", use_container_width=True)

# # Clear input if the Clear button is clicked
# if clear_button:
#     st.session_state.sql_query_input = ""
#     st.session_state.user_prompt_input = ""
#     st.rerun()

# # Execute query if the Execute button is clicked
# if execute_button and user_query:
#     with st.spinner("Running query..."):
#         try:
#             df = st.session_state.db.execute_query(user_query)
#             st.success("Query executed successfully!")

#             # Display the query and results
#             st.code(user_query, language="sql")
#             if not df.empty:
#                 st.dataframe(df, use_container_width=True)
#                 st.write(f"Rows returned: {len(df)}")
#             else:
#                 st.info(
#                     "Query executed, but no rows returned (possibly a non-SELECT query)."
#                 )

#         except Exception as err:
#             st.error(f"❌ Error running SQL: {str(err)}")

# # Close connection button
# if st.button("Close Connection", use_container_width=True):
#     st.session_state.db.close()
#     st.session_state.connected = False
#     st.success("SQL Server connection closed.")
#     st.rerun()


import streamlit as st
from sql_server import SQLServerConnection
from text_to_sql import text_to_sql
from dotenv import load_dotenv

load_dotenv()

# Connect to database
db = SQLServerConnection()
connected = db.connect()

st.title("💬 Run SQL Queries on Your Database")

if not connected:
    st.error("Failed to connect to SQL Server.")
    st.stop()

# 1️⃣ Section: Raw SQL Query
st.subheader("🛠️ Run SQL Query")
user_query = st.text_area("Enter SQL query:", height=150)

if st.button("Execute Query") and user_query:
    with st.spinner("Executing..."):
        try:
            df = db.execute_query(user_query)
            st.dataframe(df)
            st.write(f"✅ Rows returned: {len(df)}")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# 2️⃣ Section: Text-to-SQL
st.subheader("🧠 Ask a Question in Plain English")

nl_input = st.text_input(
    "Natural language question:",
    placeholder="e.g., Show all products with price > 1000",
)

if st.button("Generate SQL from Text") and nl_input:
    with st.spinner("Generating SQL..."):
        try:
            schema_df = db.get_schema()
            schema_str = db.format_schema(schema_df)
            sql_query = text_to_sql(nl_input, schema_str)
            st.code(sql_query, language="sql")

            # Optional: Execute generated SQL
            if st.button("Execute Generated SQL"):
                try:
                    df = db.execute_query(sql_query)
                    st.dataframe(df)
                    st.write(f"✅ Rows returned: {len(df)}")
                except Exception as err:
                    st.error(f"Execution error: {err}")
        except Exception as e:
            st.error(f"Failed to generate SQL: {e}")

# 3️⃣ Close button
if st.button("Close Connection"):
    db.close()
    st.success("SQL Server connection closed.")
