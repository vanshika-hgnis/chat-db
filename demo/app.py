# app.py
import streamlit as st
from db import run_sql
from llm_ollama_cloud import nl_to_sql, create_report

# ? replace the  OG chart generation with the services module
# from chart_generator import generate_chart

import pandas as pd
from services.char_service import generate_chart


st.set_page_config(page_title="AI Database Reporting", layout="wide")
st.title("AI Database Reporting")

question = st.text_input("Ask a question about your database:")

if st.button("Generate Report"):

    if not question.strip():
        st.error("Please enter a question.")
        st.stop()

    st.info("Generating SQL...")
    sql = nl_to_sql(question)
    st.code(sql, language="sql")

    #! TODO: First test it before pushing
    #     sql, columns, rows = sql_with_auto_repair(
    #     generate_sql_fn=nl_to_sql,
    #     run_sql_fn=run_sql,
    #     question=question
    # )

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
    # fig, msg = generate_chart(pd.DataFrame(data))
    fig, msg = generate_chart(pd.DataFrame(data), question)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(msg)
