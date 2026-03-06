#!/usr/bin/env python3
"""
Test admin dashboard access after login
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

def test_admin_dashboard():
    with app.test_client() as client:
        # First login as admin
        login_data = {'email': 'admin@regear.com', 'password': 'admin123'}
        login_response = client.post('/login', data=login_data)

        print(f"Login status: {login_response.status_code}")
        print(f"Login location: {login_response.headers.get('Location')}")

        # Now try to access admin dashboard
        dashboard_response = client.get('/admin/dashboard')
        print(f"Dashboard status: {dashboard_response.status_code}")

        if dashboard_response.status_code == 200:
            content = dashboard_response.get_data(as_text=True)
            if 'Dashboard Overview' in content:
                print("✅ Admin dashboard loads successfully")
                return True
            else:
                print("❌ Admin dashboard content is wrong")
                print("Content preview:", content[:300])
                return False
        elif dashboard_response.status_code == 302:
            redirect_location = dashboard_response.headers.get('Location')
            print(f"❌ Dashboard redirects to: {redirect_location}")
            return False
        else:
            print(f"❌ Dashboard failed with status: {dashboard_response.status_code}")
            content = dashboard_response.get_data(as_text=True)
            print("Error content:", content[:500])
            return False

if __name__ == "__main__":
    test_admin_dashboard()