import requests

BASE = "http://localhost:8000"

def login(username: str, password: str):
    payload = {"username": username, "password": password}
    r = requests.post(f"{BASE}/auth/login", json=payload, timeout=10)
    print("Status:", r.status_code)
    try:
        data = r.json()
        print(data)
        token = data.get("access_token")
        if token:
            print("Token length:", len(token))
    except Exception:
        print(r.text)

if __name__ == "__main__":
    login("tester", "secret123")
