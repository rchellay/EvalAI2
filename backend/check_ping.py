import requests

if __name__ == "__main__":
    try:
        r = requests.get("http://localhost:8000/ping", timeout=5)
        print(r.status_code, r.text)
    except Exception as e:
        print("ERROR", e)
