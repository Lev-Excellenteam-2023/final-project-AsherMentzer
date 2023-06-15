import subprocess
import time
from web_api import app
from web_app_client import WebAppClient


def start_web_api():
    subprocess.Popen(["python", "web_api.py"])  # Start the Web API


def start_explainer():
    subprocess.Popen(["python", "explainer.py"])  # Start the Explainer


def test_system():
    start_web_api()
    time.sleep(2)  # Wait for the Web API to start

    start_explainer()
    time.sleep(2)  # Wait for the Explainer to start

    client = WebAppClient('http://localhost:5000')
    time.sleep(10)
    # Upload a sample presentation
    file_path = r"asyncio-intro.pptx"
    uid = client.upload(file_path)
    print(f"Upload UID: {uid}")

    # Check the status of the presentation
    status = client.check_status(uid)
    assert status.is_done(), "Test Failed!!\n"
    print("Test Passed!!")
    print(f"Status: {status.status}")
    print(f"Filename: {status.filename}")
    print(f"Timestamp: {status.timestamp}")
    print(f"Explanation: {status.explanation}")


if __name__ == '__main__':
    test_system()
