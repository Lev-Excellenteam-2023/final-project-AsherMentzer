import os
import threading
import time

import web_api as web_server
from explainer import process_files
from web_app_client import WebAppClient


def test_case_1(web_client: WebAppClient):
    """
    Test Case 1:
    test unanimous upload flow
    """
    uid = web_client.upload("asyncio-intro.pptx")
    # Wait for the explainer to finish his lecture processing
    print("going to sleep to 34 seconds to for the explainer to finish his lecture processing")
    time.sleep(34)
    response = web_client.get_status(uid)
    assert response.is_done(), f"expected status was done, got {response.status}"


def test_case_2(web_client: WebAppClient):
    """
    Test Case 2:
    test upload by user flow.
    """
    web_client.upload("asyncio-intro.pptx", email="example1@gmail.com")
    # Wait for the explainer to finish his lecture processing
    print("going to sleep to 34 seconds to for the explainer to finish his lecture processing")
    time.sleep(34)
    response = web_client.get_status(email="example1@gmail.com", filename="asyncio-intro.pptx")
    assert response.is_done(), f"expected status was done, got {response.status}"


def start_explainer():
    """
    Start the explainer in a separate thread.
    """
    explainer_thread = threading.Thread(target=process_files)
    explainer_thread.daemon = True
    explainer_thread.start()


def start_server():
    """
    Start the web server in a separate thread.
    """
    server_thread = threading.Thread(target=web_server.run_web_server)
    server_thread.daemon = True
    server_thread.start()


def run_tests():
    """
    Run All test cases.
    The results of the test cases are printed.
    """

    test_cases = {"TEST_CASE_1": test_case_1,
                  "TEST_CASE_2": test_case_2}
    print("starting web api")
    start_server()

    # Wait for the server to start
    time.sleep(2)
    print("starting explainer")
    start_explainer()

    # Wait for the explainer to start
    time.sleep(2)
    web_client = WebAppClient("http://localhost:5000")

    for test_case in test_cases:
        try:
            test_cases[test_case](web_client)
            print(f"{test_case} Passed!!")
        except AssertionError as e:
            print(f"{test_case} Failed!!\n {e}")
        except Exception as e:
            print(f"{test_case} ERROR!!\n {e}")


if __name__ == "__main__":
    run_tests()
