import pymysql
import pandas as pd
import os

# MySQL database configuration
db_config = {
    'host': 'Server Name',
    'user': 'root',
    'password': 'XXXXX',
    'database': 'DB-Name',
}

# Function to import CSV into MySQL
def import_csv_to_mysql(csv_file_path, table_name):
    """
    Imports a CSV file into a MySQL table with predefined column structure.

    Args:
        csv_file_path (str): Path to the CSV file.
        table_name (str): Name of the table in the database.
    """
    # Check if file exists
    if not os.path.exists(csv_file_path):
        print(f"Error: File '{csv_file_path}' does not exist.")
        return

    # Read the CSV file into a DataFrame
    try:
        df = pd.read_csv(csv_file_path)

        # Convert date columns in YYYYMMDD format to YYYY-MM-DD
        if "date" in df.columns:
            df["date"] = df["date"].apply(lambda x: pd.to_datetime(str(x), format='%Y%m%d', errors='coerce').strftime('%Y-%m-%d') if pd.notna(x) else None)

    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    # Connect to MySQL database
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        print("Connected to the database.")
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return

    # Define the MySQL table schema
    schema = {
        "hostName": "VARCHAR(255)",
        "date": "DATE",
        "pagePath": "TEXT",
        "pageTitle": "TEXT",
        "city": "VARCHAR(255)",
        "country": "VARCHAR(255)",
        "deviceCategory": "VARCHAR(255)",
        "sessionDefaultChannelGroup": "VARCHAR(255)",
        "totalUsers": "INT",
        "newUsers": "INT",
        "sessions": "INT",
        "sessionsPerUser": "DECIMAL(10,2)",
        "screenPageViews": "INT",
        "eventCount": "INT",
        "engagementRate": "DECIMAL(10,2)",
        "engagedSessions": "INT",
        "bounceRate": "DECIMAL(10,2)",
        "averageSessionDuration": "DECIMAL(18,8)"
    }

    # Create the table
    try:
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ("
        for col, data_type in schema.items():
            create_table_sql += f"`{col}` {data_type}, "
        create_table_sql = create_table_sql.rstrip(", ") + ");"

        cursor.execute(create_table_sql)
        print(f"Table '{table_name}' created successfully.")
    except Exception as e:
        print(f"Error creating table: {e}")
        connection.close()
        return

    # Insert data into the table
    try:
        # Match DataFrame columns with the schema
        df = df[schema.keys()]

        for _, row in df.iterrows():
            row_values = tuple(row.fillna("").values)  # Replace NaN with empty strings
            placeholders = ", ".join(["%s"] * len(row))
            insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
            cursor.execute(insert_sql, row_values)

        connection.commit()
        print(f"Data imported successfully into '{table_name}' table.")
    except Exception as e:
        print(f"Error inserting data: {e}")
        connection.rollback()
    finally:
        connection.close()

# Example Usage
csv_file_path = "ga4_data_export_2024-11-01_to_2024-11-30.csv"  # Replace with your downloaded CSV file name
table_name = "ga4_export_data"  # Replace with your desired table name

import_csv_to_mysql(csv_file_path, table_name)
