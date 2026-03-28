import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Shra@0303',
    database='regear_db'
)
cursor = conn.cursor(dictionary=True)

# Check all tables with 'sub' in the name
cursor.execute("SHOW TABLES LIKE '%sub%'")
tables = cursor.fetchall()

print('========== SUBCATEGORY TABLES ==========\n')
for table_info in tables:
    table_name = list(table_info.values())[0]
    
    # Get structure
    cursor.execute(f'DESCRIBE {table_name}')
    columns = cursor.fetchall()
    
    # Get count
    cursor.execute(f'SELECT COUNT(*) as cnt FROM {table_name}')
    count = cursor.fetchone()['cnt']
    
    print(f'Table: {table_name}')
    print(f'Records: {count}')
    print('Columns:')
    for col in columns:
        print(f'  - {col["Field"]}: {col["Type"]}')
    
    # Sample data
    if count > 0:
        cursor.execute(f'SELECT * FROM {table_name} LIMIT 2')
        rows = cursor.fetchall()
        print('Sample:')
        for row in rows:
            print(f'  {row}')
    print()

cursor.close()
conn.close()
