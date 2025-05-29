# import streamlit as st
# from sql_server import SQLServerConnection  # Adjust import path
# from dotenv import load_dotenv

# load_dotenv()

# # SQL connection setup
# db = SQLServerConnection()
# connected = db.connect()

# st.title("💬 Run SQL Queries on Your Database")

# if not connected:
#     st.error("Failed to connect to SQL Server. Check logs.")
#     st.stop()

# # User input: SQL Query (Text Area for better readability)
# user_query = st.text_area(
#     "Enter your SQL Query:",
#     placeholder="Example: SELECT * FROM customers WHERE country = 'USA'",
#     height=150,
# )

# # Execute button
# if st.button("Execute Query") and user_query:
#     with st.spinner("Running query..."):
#         try:
#             df = db.execute_query(user_query)
#             st.success("Query executed successfully!")

#             # Display results
#             st.code(user_query, language="sql")  # Show the SQL query
#             st.dataframe(df)  # Show the DataFrame

#             # Optional: Show row count
#             st.write(f"Rows returned: {len(df)}")

#         except Exception as err:
#             st.error(f"❌ Error running SQL: {str(err)}")

# # Close connection on shutdown
# if st.button("Close Connection"):
#     db.close()
#     st.success("SQL Server connection closed.")


import streamlit as st
from sql_server import SQLServerConnection
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use session state to manage the database connection
if "db" not in st.session_state:
    st.session_state.db = SQLServerConnection()
    st.session_state.connected = st.session_state.db.connect()

# Main UI
st.title("💬 ChatDB: Run SQL Queries on Your Database")
st.markdown("Enter a SQL query below to interact with your SQL Server database.")

if not st.session_state.connected:
    st.error("Failed to connect to SQL Server. Check logs for details.")
    st.stop()

# Fetch available tables for the dropdown
tables = st.session_state.db.get_table_schemas()
selected_table = st.selectbox("Select a table to query (optional):", [""] + tables)

# User input: SQL Query
user_query = st.text_area(
    "Enter your SQL Query:",
    placeholder=f"Example: SELECT * FROM {selected_table if selected_table else 'your_table'} LIMIT 5",
    height=150,
    key="sql_query_input",
)

# Layout for buttons
col1, col2 = st.columns(2)
with col1:
    execute_button = st.button("Execute Query", use_container_width=True)
with col2:
    clear_button = st.button("Clear Input", use_container_width=True)

# Clear input if the Clear button is clicked
if clear_button:
    st.session_state.sql_query_input = ""
    st.rerun()

# Execute query if the Execute button is clicked
if execute_button and user_query:
    with st.spinner("Running query..."):
        try:
            df = st.session_state.db.execute_query(user_query)
            st.success("Query executed successfully!")

            # Display the query and results
            st.code(user_query, language="sql")
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                st.write(f"Rows returned: {len(df)}")
            else:
                st.info(
                    "Query executed, but no rows returned (possibly a non-SELECT query)."
                )

        except Exception as err:
            st.error(f"❌ Error running SQL: {str(err)}")

# Close connection button
if st.button("Close Connection", use_container_width=True):
    st.session_state.db.close()
    st.session_state.connected = False
    st.success("SQL Server connection closed.")
    st.rerun()
