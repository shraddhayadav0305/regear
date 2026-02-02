#!/usr/bin/env python3
"""Run Flask app for ReGear"""
import sys
import io

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import app

if __name__ == "__main__":
    print("🚀 Starting ReGear Server...")
    print("📍 Server running at: http://localhost:5000")
    print("🔐 Login at: http://localhost:5000/login")
    print("   Admin: admin@regear.com / admin123")
    print("   Buyer: buyer@test.com / buyer123")
    print("\nPress CTRL+C to quit\n")
    app.run(host='localhost', port=5000, debug=False, use_reloader=False)
