class IntentClassifier:
    def __init__(self):
        self.keywords = {
            "data_view": ["show", "view", "table", "display"],
            "data_analysis": [
                "mean",
                "average",
                "sum",
                "count",
                "correlation",
                "describe",
            ],
            "data_visualization": ["plot", "graph", "chart", "visualize"],
            "sql_query": [
                "query",
                "select",
                "update",
                "delete",
                "insert",
                "from",
                "where",
            ],
        }

    def classify(self, text):
        text_lower = text.lower()
        for intent, words in self.keywords.items():
            if any(word in text_lower for word in words):
                return intent
        return "sql_query"  # default
