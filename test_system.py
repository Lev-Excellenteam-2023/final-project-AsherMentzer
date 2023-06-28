import threading
import time
import web_api as web_server
from explainer import process_files
from web_app_client import WebAppClient


def test_system():
    """
    Run the test scenario.
    This function starts the web server and the explainer in separate threads, performs an upload, waits for the
    explainer to finish processing the lecture, and retrieves the status. It then asserts that the process of
    explaining the lecture is done and prints the test result.
    """

    server_thread = threading.Thread(target=web_server.run_web_server)
    server_thread.start()
    # Wait for the server to start
    time.sleep(2)
    explainer_thread = threading.Thread(target=process_files)
    explainer_thread.start()
    # Wait for the explainer to start
    time.sleep(2)
    web_client = WebAppClient("http://localhost:5000")
    uid = web_client.upload("asyncio-intro.pptx")
    # Wait for the explainer to finish his lecture processing
    time.sleep(15)
    print("check status")
    response = web_client.check_status(uid)
    print("finish check status")
    assert response.is_done(), "Test Failed!!\n" \
                               "Something went wrong - the process of explaining the lecture did not finished"
    print("Test Passed!!")


if __name__ == '__main__':
    test_system()
