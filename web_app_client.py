import time

import requests
import json
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, Union


@dataclass
class Status:
    """
    Represents the status of an uploaded presentation.

    Attributes:
        status (str): The status of the upload.
        filename (str): The original filename of the presentation.
        timestamp (datetime): The timestamp of the upload.
        explanation (Optional[str]): The explanation of the upload, if available.
    """

    status: str
    filename: str
    timestamp: datetime
    explanation: Optional[str]

    def is_done(self) -> bool:
        """
        Checks if the status is 'done'.

        Returns:
            bool: True if the status is 'done', False otherwise.
        """
        return self.status == 'done'


class WebAppClient:
    """
    Client for interacting with the Web API.

    Args:
        base_url (str): The base URL of the Web API.

    Attributes:
        base_url (str): The base URL of the Web API.
    """

    def __init__(self, base_url: str):
        """
        Initializes the WebAppClient with the base URL of the Web API.

        Args:
            base_url (str): The base URL of the Web API.
        """
        self.base_url = base_url

    def upload(self, file_path: str, email: str = None) -> str:
        """
        Uploads a file to the Web API.

        Args:
            file_path (str): The path of the file to upload.

        Returns:
            str: The UID of the upload.
        Raises:
            requests.HTTPError: If the upload request fails.
            :param file_path:
            :param email:
        """
        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                data = {"email": email} if email else None
                response = requests.post(f"{self.base_url}/upload", files=files, data=data)
                response_json = response.json()
                if response.ok:
                    return response_json['uid']
                else:
                    raise Exception(f"Upload failed: {response_json.get('error')}")
        except Exception as e:
            raise Exception(f"Upload failed: {str(e)}")

    def get_status(self, uid: str = None, email: str = None, filename: str = None) -> Status:
        """
        Get the status of a request by UID or by email and a filename.
        :param filename: The name of the file uploaded.
        :param email: The email address used during the upload.
        :param uid: The unique identifier (UID) of the request.
        :return: Status Object representing the status of the request.
        :raises Exception: If the status request fails.
        """
        try:
            if uid:
                upload_identified = uid
            elif email and filename:
                upload_identified = f"{filename} {email}"
            else:
                raise Exception(f"Status request failed: no upload identified provided")
            response = requests.get(f"{self.base_url}/status/{upload_identified}")
            response_json = response.json()
            if response.ok:
                status = response_json['status']
                filename = response_json['filename']
                timestamp = response_json['upload_time']
                explanation = []
                if response_json['status'] == 'done':
                    explanation = response_json['explanation']
                return Status(status, filename, timestamp, explanation)
            else:
                raise Exception(f"Status request failed")
        except Exception as e:
            raise Exception(f"Status request failed: {str(e)}")

    def check_status_for_user(self, file_name: str, email: str) -> Status:
        """
        Retrieves the status of an upload from the Web API.

        Args:
            file_name (str): The file name.
            email (str): The user email.
        Returns:
            Status: The status of the upload.
        Raises:
            requests.HTTPError: If the status request fails.
        """
        url = f"{self.base_url}/status/{file_name + email}"
        response = requests.get(url)

        if response.ok:
            response_data = json.loads(response.text)
            return self.parse_status(response_data)
        else:
            response.raise_for_status()

    def parse_status(self, response_data: Dict[str, Union[str, int]]) -> Status:
        """
        Parses the status response data into a Status object.

        Args:
            response_data (Dict[str, Union[str, int]]): The response data from the Web API.

        Returns:
            Status: The parsed status object.
        """
        status = response_data['status']
        filename = response_data['filename']
        timestamp = datetime.fromtimestamp(response_data['timestamp'])
        explanation = response_data['explanation']

        return Status(status, filename, timestamp, explanation)


def run_web_app():
    client = WebAppClient('http://localhost:5000')

    # Upload a file and get the UID
    uid = client.upload(r"C:\Networks\final_project_test\asyncio-intro.pptx")
    print(f"Upload UID: {uid}")
    time.sleep(40)
    # Get the status of an upload
    status = client.check_status(uid)
    if status.is_done():
        print("Upload is done!")
        print(f"Filename: {status.filename}")
        print(f"Timestamp: {status.timestamp}")
        print(f"Explanation: {status.explanation}")
    else:
        print("Upload is still pending.")


if __name__ == "__main__":
    run_web_app()
