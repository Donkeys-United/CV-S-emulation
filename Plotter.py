import sqlite3
import matplotlib.pyplot as plt
import pandas as pd

def fetch_data_from_db(database_path, table_name, column_id, column_time, column_value, ids):
    """
    Fetches data from the SQLite database based on the given IDs.

    Parameters:
    - database_path: Path to the SQLite database file.
    - table_name: Name of the table to query.
    - column_id: Column name for the ID field.
    - column_time: Column name for the time field.
    - column_value: Column name for the value to plot.
    - ids: List of IDs to filter data.

    Returns:
    - A Pandas DataFrame with the filtered data.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(database_path)
        
        # Create a SQL query
        query = f"""
        SELECT {column_time}, {column_value}, {column_id}
        FROM {table_name}
        WHERE {column_id} IN ({', '.join(['?'] * len(ids))})
        """

        # Execute the query and fetch the data
        df = pd.read_sql_query(query, conn, params=ids)
        conn.close()

        return df
    except Exception as e:
        print(f"Error: {e}")
        return None

def plot_data(df, column_time, column_value, column_id):
    """
    Plots the data using Matplotlib.

    Parameters:
    - df: Pandas DataFrame with the data to plot.
    - column_time: Column name for the time field.
    - column_value: Column name for the value field.
    - column_id: Column name for the ID field.
    """
    try:
        plt.figure(figsize=(10, 6))
        
        # Loop through each unique ID and plot its data
        for id_ in df[column_id].unique():
            subset = df[df[column_id] == id_]
            plt.plot(subset[column_time], subset[column_value], label=f'ID {id_}')

        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.title('Data Plot over Time')
        plt.legend()
        plt.grid(True)
        plt.show()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # User-defined variables
    database_path = "example.db"  # Path to your SQLite database file
    table_name = "your_table"     # Name of the table to query
    column_id = "id"              # ID column name
    column_time = "time"          # Time column name
    column_value = "value"        # Value column name

    # IDs to filter data
    ids = [1, 2, 3]

    # Fetch data
    data = fetch_data_from_db(database_path, table_name, column_id, column_time, column_value, ids)

    if data is not None:
        # Convert the time column to datetime for better plotting
        data[column_time] = pd.to_datetime(data[column_time])

        # Plot data
        plot_data(data, column_time, column_value, column_id)
