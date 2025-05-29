import re


class IntentClassifier:
    def __init__(self):
        # Define intent patterns (keyword-based)
        self.intent_patterns = {
            "data_table": ["show", "select", "list", "get", "display", "table"],
            "data_analysis": [
                "average",
                "sum",
                "count",
                "group by",
                "aggregate",
                "analyze",
            ],
            "data_visualization": ["plot", "chart", "graph", "visualize", "draw"],
            "db_related": ["create", "update", "delete", "insert", "drop", "alter"],
        }

    def classify_intent(self, prompt):
        """Classify the intent of the user prompt"""
        prompt = prompt.lower().strip()

        # Check for each intent type based on keywords
        for intent, keywords in self.intent_patterns.items():
            for keyword in keywords:
                if re.search(r"\b" + keyword + r"\b", prompt):
                    return intent

        # Default to data_table if no specific intent is matched
        return "data_table"
