from sql_server import SQLServerConnection

def main():
    db = SQLServerConnection()
    
    if not db.connect():
        print("Failed to connect to database")
        return
    
    try:
        # Example: Get SQL Server version
        print("\nGetting SQL Server version...")
        version = db.execute_query("SELECT @@VERSION AS version")
        print(version)
        
        # Example: Get database tables
        print("\nListing database tables...")
        tables = db.execute_query("""
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        """)
        print(tables)
        
        # Example: Simple query from a table (replace 'YourTable' with actual table)
        print("\nSample data from a table...")
        try:
            sample_data = db.execute_query("SELECT TOP 5 * FROM product")
            print(sample_data)
        except Exception as e:
            print(f"Couldn't fetch sample data: {str(e)}")
            print("This is normal if 'YourTable' doesn't exist")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()