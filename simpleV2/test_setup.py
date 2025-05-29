#!/usr/bin/env python3
"""
Simple test script to verify the Flask application setup is correct.
This script tests the import structure without requiring a database connection.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all major modules can be imported."""
    try:
        print("Testing imports...")
        
        # Test extensions
        from extensions import db, login_manager, bcrypt, limiter
        print("✓ Extensions imported successfully")
        
        # Test models  
        from models import User, Transaction
        print("✓ Models imported successfully")
        
        # Test forms
        from forms import LoginForm, RegistrationForm, TransferForm
        print("✓ Forms imported successfully")
        
        # Test PSGC API
        import psgc_api
        print("✓ PSGC API imported successfully")
        
        # Test app creation (without database connection)
        os.environ['MYSQL_HOST'] = 'dummy'
        os.environ['MYSQL_USER'] = 'dummy'
        os.environ['MYSQL_DATABASE'] = 'dummy'
        
        from app import create_app
        app = create_app()
        print("✓ App created successfully")
        
        print("\n🎉 All imports successful! The application structure is correct.")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_structure():
    """Test that models have the correct fields matching the schema."""
    try:
        from models import User, Transaction
        
        print("\nTesting model structure...")
        
        # Test User model fields
        user_fields = [
            'id', 'username', 'email', 'firstname', 'lastname',
            'address_line', 'region_code', 'region_name', 
            'province_code', 'province_name', 'city_code', 'city_name',
            'barangay_code', 'barangay_name', 'postal_code', 'phone',
            'password_hash', 'account_number', 'balance', 'status',
            'is_admin', 'is_manager', 'date_registered'
        ]
        
        user_model_attrs = [attr for attr in dir(User) if not attr.startswith('_')]
        missing_fields = []
        
        for field in user_fields:
            if not hasattr(User, field):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ User model missing fields: {missing_fields}")
            return False
        else:
            print("✓ User model has all required fields")
        
        # Test Transaction model fields
        transaction_fields = ['id', 'sender_id', 'receiver_id', 'amount', 'timestamp', 'transaction_type', 'details']
        
        transaction_missing = []
        for field in transaction_fields:
            if not hasattr(Transaction, field):
                transaction_missing.append(field)
        
        if transaction_missing:
            print(f"❌ Transaction model missing fields: {transaction_missing}")
            return False
        else:
            print("✓ Transaction model has all required fields")
        
        print("✓ Model structure matches schema requirements")
        return True
        
    except Exception as e:
        print(f"❌ Model structure test failed: {e}")
        return False

def test_forms_structure():
    """Test that forms are properly structured."""
    try:
        from forms import LoginForm, RegistrationForm, TransferForm, UserEditForm
        
        print("\nTesting forms structure...")
        
        # Test that forms can be instantiated
        login_form = LoginForm()
        print("✓ LoginForm can be instantiated")
        
        reg_form = RegistrationForm()
        print("✓ RegistrationForm can be instantiated")
        
        transfer_form = TransferForm()
        print("✓ TransferForm can be instantiated")
        
        user_edit_form = UserEditForm(original_email="test@example.com")
        print("✓ UserEditForm can be instantiated")
        
        print("✓ All forms are properly structured")
        return True
        
    except Exception as e:
        print(f"❌ Forms structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Simple Banking App Setup")
    print("=" * 50)
    
    success = True
    
    # Run tests
    success &= test_imports()
    success &= test_model_structure() 
    success &= test_forms_structure()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! The application setup is correct.")
        print("\nNext steps:")
        print("1. Set up a MySQL database")
        print("2. Update the .env file with correct database credentials")
        print("3. Run 'python init_db.py' to initialize the database")
        print("4. Run 'python app.py' to start the application")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
