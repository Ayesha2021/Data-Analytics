import pandas as pd
import mysql.connector
import os

# List of CSV Files and their correpsonding SQL table names

csv_files = [

    ('customers.csv', 'customers'),
    ('orders.csv', 'orders'),
    ('sellers.csv', 'sellers'),
    ('products.csv', 'products'),
    ('geolocation.csv', 'geolocation'),
    ('payments.csv', 'payments'),
    ('order_items.csv', 'order_items'),

]

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='admin',
    database='target_db'
)
cursor = conn.cursor()

folder_path = '.'


def get_sql_type(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return 'INT'
    elif pd.api.types.is_float_dtype(dtype):
        return 'FLOAT'
    elif pd.api.types.is_bool_dtype(dtype):
        return 'BOOLEAN'
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return 'DATETIME'
    else:
        return 'TEXT'


for csv_file, table_name in csv_files:
    file_path = os.path.join(folder_path, csv_file)
    # Replace NaN with None to handle SQL null

    # read the csv file
    print('file path `{file_path}`')
    df = pd.read_csv(file_path)
    # df = df.where(pd.notnull(df), None)
    df = df.where(pd.notnull(df), None)
    print('Processing CSV File {csv_file}')
    # Clean column names
    df.columns = [col.replace(' ', '_').replace(
        '-', '_').replace('.', '_') for col in df.columns]

    # Generate the CREATE TABLE statement with appropriate data types
    df.columns = [col.replace(' ', '_').replace(
        '-', '_').replace('.', '_') for col in df.columns]
    columns = ', '.join(
        [f'`{col}` {get_sql_type(df[col].dtype)}' for col in df.columns])
    create_table_query = f'CREATE TABLE IF NOT EXIST `{table_name}` ({columns})'
    cursor.execute(create_table_query)
    # cursor = conn.execute(create_able_query)
    # Insert DataFrame data into the MySQL table
    for _, row in df.iterrows():
        # convert row to tuple and handle NaN/None explicitly
        values = tuple(None if pd.isna(x) else x for x in row)

        sql = f"INSERT INTO `{table_name}` ({', '.join(['`' + col + '`' for col in df.columns])}) VALUES ({', '.join(['%s'] * len(row))})"
        # sql = f"insert into `{table_name}` ({','.join(['`'+col+'`' for col in df.columns])}) values ({','.join(['%s'] * len(row))})"
        cursor.execute(sql, values)
    conn.commit()

    conn.close()
