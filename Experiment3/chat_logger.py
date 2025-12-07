import csv
from datetime import datetime
import os


class ChatLogger:
    def __init__(self, logfile="chat_logs.csv"):
        self.logfile = logfile
        if not os.path.exists(logfile):
            with open(logfile, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "intent", "prompt", "sql", "result"])

    def log(self, intent, prompt, sql, result):
        with open(self.logfile, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), intent, prompt, sql, str(result)])
