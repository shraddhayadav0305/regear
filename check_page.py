import requests

response = requests.get('http://localhost:5000/listing/6')
print('Status:', response.status_code)

# Find the views section
lines = response.text.split('\n')
for i, line in enumerate(lines):
    if 'Views' in line:
        print(f'Line {i}: {line.strip()}')
        if i + 1 < len(lines):
            print(f'Line {i+1}: {lines[i+1].strip()}')
        break

# Also check the database
import mysql.connector
conn = mysql.connector.connect(host='localhost', user='root', password='Shra@0303', database='regear_db')
cursor = conn.cursor()
cursor.execute('SELECT view_count FROM listings WHERE id = 6')
result = cursor.fetchone()
print('Database view_count:', result[0])
cursor.close()
conn.close()