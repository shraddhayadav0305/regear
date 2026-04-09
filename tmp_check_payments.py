import mysql.connector

conn = mysql.connector.connect(host='localhost', user='root', password='Shra@0303', database='regear_db')
cur = conn.cursor(dictionary=True)
q = """
SELECT p.id, p.user_id, p.amount, p.method as payment_method,
       COALESCE(p.status, st.payment_status) as status, p.created_at as paid_at,
       u.username, u.email,
       COALESCE(bp.name, CONCAT('Subscription Plan - ', st.plan_name)) as package_name,
       CASE WHEN bp.name IS NOT NULL THEN 'Boost' ELSE 'Subscription' END as transaction_type,
       l.status as listing_status,
       COALESCE(b.status, '') as promotion_status
FROM payments p
JOIN users u ON p.user_id = u.id
LEFT JOIN listings l ON l.id = p.ad_id
LEFT JOIN boost_packages bp ON bp.id = p.package_id
LEFT JOIN subscription_transactions st ON st.transaction_id = p.transaction_id AND st.user_id = p.user_id
LEFT JOIN ad_boosts b ON b.payment_id = p.id
ORDER BY p.created_at DESC
LIMIT 200
"""
cur.execute(q)
rows = cur.fetchall()
print('rows', len(rows))
for row in rows[:3]:
    print(row)
cur.close()
conn.close()
