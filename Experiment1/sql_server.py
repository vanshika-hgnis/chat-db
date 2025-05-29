#

import pyodbc
import pandas as pd
from dotenv import load_dotenv
import os
import logging


class SQLServerConnection:
    def __init__(self):
        load_dotenv()
        self.connection = None
        self._setup_logging()

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("sql_server.log"), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def connect(self):
        """Establish database connection optimized for SQL Server 2014"""
        try:
            server = os.getenv("DB_SERVER")
            database = os.getenv("DB_NAME")
            username = os.getenv("DB_USER")
            password = os.getenv("DB_PASSWORD")

            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                "Encrypt=no;"
                "Trusted_Connection=no;"
                "TrustServerCertificate=yes;"
                "Connection Timeout=30;"
            )

            self.logger.info("Attempting connection to SQL Server...")
            self.connection = pyodbc.connect(conn_str)
            self.logger.info("Successfully connected to SQL Server")
            return True
        except pyodbc.Error as e:
            self.logger.error(f"Connection failed (SQL State: {e.sqlstate}): {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return False

    def is_connected(self):
        """Check if the connection is active"""
        return self.connection is not None

    def get_table_schemas(self):
        """Fetch the list of tables and their schemas"""
        try:
            query = """
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            """
            tables_df = self.execute_query(query)
            tables = tables_df["TABLE_NAME"].tolist()
            return tables
        except Exception as e:
            self.logger.error(f"Failed to fetch table schemas: {str(e)}")
            return []

    def execute_query(self, query, params=None):
        """Execute a SQL query and return results as DataFrame"""
        if not self.is_connected():
            raise Exception("Not connected to the database")

        try:
            self.logger.info(f"Executing query: {query}")
            cursor = self.connection.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Check if the query returns results (e.g., SELECT)
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                data = cursor.fetchall()
                df = pd.DataFrame.from_records(data, columns=columns)
            else:
                # For non-SELECT queries (e.g., INSERT, UPDATE)
                self.connection.commit()
                df = pd.DataFrame()  # Return empty DataFrame for non-SELECT queries

            self.logger.info(f"Query executed successfully. Rows affected: {len(df)}")
            return df

        except Exception as e:
            self.logger.error(f"Query failed: {str(e)}")
            raise
        finally:
            if "cursor" in locals():
                cursor.close()

    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.logger.info("Connection closed")
            self.connection = None
