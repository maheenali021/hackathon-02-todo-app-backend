import asyncio
import json
from http.client import HTTPConnection

# Test the backend server by making a simple request
def test_chat_endpoint():
    try:
        conn = HTTPConnection("127.0.0.1", 8000, timeout=10)

        # First test the health endpoint
        print("Testing health endpoint...")
        conn.request("GET", "/health")
        response = conn.getresponse()
        print(f"Health endpoint status: {response.status}")
        print(f"Health endpoint response: {response.read().decode()}")

        conn.close()
    except Exception as e:
        print(f"Error testing endpoints: {e}")

if __name__ == "__main__":
    test_chat_endpoint()