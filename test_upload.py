import requests

# Replace this URL with the actual URL of your Flask server
UPLOAD_URL = 'http://localhost:5000/upload'

#b'{"uid":"239707b7-1476-46fe-a70f-d4acbf14d910"}\n'
def test_upload_file():
    # Open the file you want to upload
    with open('asyncio-intro.pptx', 'rb') as file:
        # Create a dictionary for the files parameter (key should match the form field name in your HTML form)
        files = {'file': file}
        # Send the POST request to the server
        response = requests.post(UPLOAD_URL, files=files)

    # Assert that the status code is what you expect (e.g., 200 for success)
    assert response.status_code == 200
    # Optionally, you can assert other conditions based on your function's behavior
    # For example, you can check if the response contains specific data or headers


# Replace this URL with the actual URL of your Flask server
STATUS_URL = 'http://localhost:5000/status/'


def test_get_status(uid='239707b7-1476-46fe-a70f-d4acbf14d910'):
    # Replace 'some_uid' with the UID you want to test
    # Send the GET request to the server
    response = requests.get(STATUS_URL + "uid=" +uid)

    # Assert that the status code is what you expect (e.g., 200 for success)
    assert response.status_code == 200
    # Optionally, you can assert other conditions based on your function's behavior
    # For example, you can check if the response contains specific data or headers


if __name__ == '__main__':
    test_get_status('ee6bf9aa-4d78-4f17-9d7c-bffa2239b7b3')
