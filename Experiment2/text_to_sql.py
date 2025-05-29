from ollama import Client

client = Client(host="http://localhost:11434")  # Default Ollama endpoint


def text_to_sql(nl_query, schema_str):
    """Use LLaMA3 via Ollama to convert natural language to SQL query."""
    prompt = f"""
You are an expert SQL generator.

Here is the database schema:
{schema_str}

Convert the following request into a SQL query:
"{nl_query}"

Only return the SQL query. Do not include explanations or formatting.
"""

    response = client.chat(
        model="llama3.2:1b",
        messages=[
            {"role": "system", "content": "You are a SQL assistant."},
            {"role": "user", "content": prompt},
        ],
    )

    return response["message"]["content"].strip()
