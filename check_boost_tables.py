import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Shra@0303',
    database='regear_db'
)
cursor = conn.cursor(dictionary=True)

# Check if boost tables exist
cursor.execute("SHOW TABLES LIKE '%boost%'")
tables = cursor.fetchall()

print('BOOST-RELATED TABLES:')
for table_info in tables:
    table_name = list(table_info.values())[0]
    print(f'\nTable: {table_name}')
    
    cursor.execute(f'DESCRIBE {table_name}')
    columns = cursor.fetchall()
    print('Columns:')
    for col in columns:
        print(f'  - {col["Field"]}: {col["Type"]}')
    
    # Sample data
    cursor.execute(f'SELECT COUNT(*) as cnt FROM {table_name}')
    count = cursor.fetchone()['cnt']
    print(f'Records: {count}')

cursor.close()
conn.close()
