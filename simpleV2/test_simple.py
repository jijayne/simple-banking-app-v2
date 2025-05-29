#!/usr/bin/env python3
import os
import sys

print("🧪 Testing Simple Banking App Setup")
print("=" * 50)

# Set dummy environment variables to avoid database connection issues
os.environ['MYSQL_HOST'] = 'dummy'
os.environ['MYSQL_USER'] = 'dummy'  
os.environ['MYSQL_DATABASE'] = 'dummy'
os.environ['SECRET_KEY'] = 'test-key'

try:
    print("1. Testing extensions...")
    from extensions import db, login_manager, bcrypt, limiter
    print("   ✓ Extensions imported successfully")

    print("2. Testing models...")
    from models import User, Transaction
    print("   ✓ Models imported successfully")

    print("3. Testing forms...")
    from forms import LoginForm, RegistrationForm, TransferForm
    print("   ✓ Forms imported successfully")

    print("4. Testing PSGC API...")
    import psgc_api
    print("   ✓ PSGC API imported successfully")

    print("5. Testing app creation...")
    from app import create_app
    app = create_app()
    print("   ✓ App created successfully")

    print("\n🎉 All tests passed! Application setup is correct.")
    print("\nNext steps to run the application:")
    print("1. Set up a MySQL database")
    print("2. Update .env file with correct database credentials")
    print("3. Run: python init_db.py")
    print("4. Run: python app.py")

except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
