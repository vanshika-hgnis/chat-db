# app.py
import streamlit as st
from db import run_sql
from llm_ollama_cloud import nl_to_sql, create_report
from chart_generator import generate_chart
import pandas as pd

st.set_page_config(page_title="Cloud AI SQL Reporting", layout="wide")
st.title("Cloud AI SQL Reporting (Ollama Cloud)")

question = st.text_input("Ask a question about your database:")

if st.button("Generate Report"):

    if not question.strip():
        st.error("Please enter a question.")
        st.stop()

    st.info("Generating SQL...")
    sql = nl_to_sql(question)
    st.code(sql, language="sql")

    try:
        columns, rows = run_sql(sql)
    except Exception as e:
        st.error(f"SQL Execution Error: {e}")
        st.stop()

    data = [dict(zip(columns, r)) for r in rows]

    st.subheader("Raw Data")
    st.dataframe(data, use_container_width=True)

    st.info("Generating report...")
    report = create_report(question, data)

    st.subheader("Report")
    st.write(report)

    st.subheader("Charts")
    fig, msg = generate_chart(pd.DataFrame(data))
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(msg)
