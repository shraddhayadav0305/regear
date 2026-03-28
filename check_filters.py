import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Shra@0303',
    database='regear_db'
)
cursor = conn.cursor(dictionary=True)

# Check all tables
cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='regear_db'")
tables = cursor.fetchall()
print('====== TABLES IN DATABASE ======')
for t in tables:
    print(f'  {t["TABLE_NAME"]}')

# Check if filter_options table exists
cursor.execute("SHOW TABLES LIKE 'filter%'")
filter_tables = cursor.fetchall()

if filter_tables:
    print('\n====== FILTER TABLES FOUND ======')
    for table_name in filter_tables:
        table = list(table_name.values())[0]
        print(f'\nTable: {table}')
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        if rows:
            print(f'  Total records: {len(rows)}')
            # Show first 5
            for row in rows[:5]:
                print(f'    {row}')
        else:
            print('  (Empty)')
else:
    print('\n❌ No filter tables found')

cursor.close()
conn.close()
