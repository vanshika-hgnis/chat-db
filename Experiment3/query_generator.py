import subprocess
import json


class SQLQueryGenerator:
    def __init__(self, model_name="llama2:7b"):
        self.model_name = model_name

    def generate_sql(self, prompt, schema_context=""):
        full_prompt = f"""
You are a SQL assistant. Based on the schema: 
{schema_context}

Translate the following user question to SQL:
'{prompt}'

SQL:"""

        command = ["ollama", "run", self.model_name, "--json"]
        result = subprocess.run(
            command, input=full_prompt.encode(), capture_output=True
        )

        if result.returncode == 0:
            try:
                response = result.stdout.decode().strip()
                return response.split("SQL:")[-1].strip()
            except:
                return "Could not parse SQL"
        else:
            return f"Ollama error: {result.stderr.decode()}"
