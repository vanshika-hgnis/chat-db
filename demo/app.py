import streamlit as st
from db import run_sql
from llm_ollama_cloud import nl_to_sql, create_report  # updated import


st.title("Cloud AI SQL Reporting (Ollama Cloud)")

question = st.text_input("Ask a question about your database:")

TABLE_SCHEMA = """
Tables:
  Employees(id, name, department, salary)
  Sales(order_id, date, amount, customer)
"""

if st.button("Generate Report"):

    if not question.strip():
        st.error("Please type a question.")
        st.stop()

    st.write("Generating SQL using Ollama Cloud...")
    sql = nl_to_sql(question, TABLE_SCHEMA)

    st.code(sql, language="sql")

    try:
        columns, rows = run_sql(sql)
    except Exception as e:
        st.error(f"SQL Error: {e}")
        st.stop()

    data = [dict(zip(columns, r)) for r in rows]

    st.write("Data:")
    st.dataframe(data)

    st.write("Generating Report...")
    report = create_report(question, data)

    st.subheader("Report")
    st.write(report)
