
import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api/auth"

def register():
    print("--- Registering ---")
    data = {
        "email": "debug_user_001@example.com",
        "username": "debug_user_001",
        "password": "Password123!",
        "full_name": "Debug User"
    }
    try:
        r = requests.post(f"{BASE_URL}/register", json=data)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        if r.status_code == 201 or "already registered" in r.text or "Using" in r.text: # Handle re-runs
             return True
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def login_username():
    print("\n--- Login with Username ---")
    # Using data directly as requests handles form-encoding for 'data' arg
    data = {
        "username": "debug_user_001",
        "password": "Password123!"
    }
    try:
        r = requests.post(f"{BASE_URL}/login", data=data)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

def login_email():
    print("\n--- Login with Email ---")
    data = {
        "username": "debug_user_001@example.com", # OAuth2 form expects 'username' field to carry the identifier
        "password": "Password123!"
    }
    try:
        r = requests.post(f"{BASE_URL}/login", data=data)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if register():
        login_username()
        login_email()
