from types import SimpleNamespace
from routes.admin import get_db_connection, compute_filtered_transactions

conn = get_db_connection()
cur = conn.cursor(dictionary=True)
result = compute_filtered_transactions(cur, SimpleNamespace(get=lambda k, default='': ''))
print('success:', result['success'])
print('stats:', result['stats'])
print('transactions loaded:', len(result['transactions']))
print('chart keys:', list(result['charts'].keys()))
cur.close()
conn.close()
