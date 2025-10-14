import requests

BASE = "http://localhost:8000"

def register(username: str, email: str, password: str):
    payload = {"username": username, "email": email, "password": password}
    r = requests.post(f"{BASE}/auth/register", json=payload, timeout=10)
    print("Status:", r.status_code)
    try:
        print(r.json())
    except Exception:
        print(r.text)

if __name__ == "__main__":
    # Change values if you want another test user
    register("tester", "tester@example.com", "secret123")
