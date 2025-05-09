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
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        """Establish database connection optimized for SQL Server 2014"""
        try:
            server = os.getenv('DB_SERVER')  # e.g., 'localhost\\SQLEXPRESS'
            database = os.getenv('DB_NAME')
            username = os.getenv('DB_USER')
            password = os.getenv('DB_PASSWORD')
            
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                "Encrypt=no;"  # Important for SQL Server 2014
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
    
    def execute_query(self, query, params=None):
        """Execute a SQL query and return results as DataFrame"""
        try:
            cursor = self.connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            # Get column names from cursor description
            columns = [column[0] for column in cursor.description]
            
            # Fetch all rows
            data = cursor.fetchall()
            
            # Create DataFrame
            df = pd.DataFrame.from_records(data, columns=columns)
            return df
            
        except Exception as e:
            self.logger.error(f"Query failed: {str(e)}")
            raise
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.logger.info("Connection closed")
            self.connection = None