from datetime import datetime
import os
import json
import time
import uuid

from flask import Flask, request, jsonify

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER


@app.route('/upload', methods=['POST'])
def upload():
    """
    API endpoint for uploading a file.

    Returns:
        flask.Response: JSON response containing the UID of the upload.
    """
    if not os.path.isdir(app.config['UPLOAD_FOLDER']):
        os.mkdir(app.config['UPLOAD_FOLDER'])

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided.'}), 400

    file = request.files['file']
    uid = generate_uid()
    filename = get_filename(file.filename)
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')  # int(time.time())
    new_filename = f"{filename}_{timestamp}_{uid}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
    file.save(file_path)
    response = {'uid': uid}
    return jsonify(response)


@app.route('/status/<uid>', methods=['GET'])
def status(uid):
    """
    API endpoint for checking the status of an upload.

    Args:
        uid (str): The UID of the upload.

    Returns:
        flask.Response: JSON response containing the status, filename, timestamp, and explanation of the upload.
    """
    print(uid)
    file_path = find_file_by_uid(uid)

    if file_path is None:
        response = {
            'status': 'not found',
            'filename': '',
            'timestamp': '',
            'explanation': None
        }
        return jsonify(response), 404

    file_status = get_status(file_path)
    print("bug check")
    filename, timestamp, explanation = get_file_details(file_path, file_status)

    response = {
        'status': file_status,
        'filename': filename,
        'timestamp': timestamp,
        'explanation': explanation
    }

    if file_status == 'done':
        output_file = get_output_file(file_path)
        if output_file:
            output_data = parse_output_file(output_file)
            response.update(output_data)

    return jsonify(response)


def generate_uid():
    """
    Generates a unique identifier (UID) for an upload.

    Returns:
        str: The generated UID.
    """
    return str(uuid.uuid4())


def get_filename(filename):
    """
    Extracts the filename without the extension.

    Args:
        filename (str): The original filename.

    Returns:
        str: The filename without the extension.
    """
    return os.path.splitext(filename)[0]


def find_file_by_uid(uid):
    """
    Finds the file path associated with a given UID.

    Args:
        uid (str): The UID of the upload.

    Returns:
        str: The file path if found, or None if not found.
    """
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        if uid in file:
            return os.path.join(app.config['UPLOAD_FOLDER'], file)
    return None


def get_status(file_path):
    """
    Determines the status of an upload based on the presence of an output file.

    Args:
        file_path (str): The file path of the upload.

    Returns:
        str: The status of the upload ('done' or 'pending').
    """
    output_file = get_output_file(file_path)
    if output_file:
        return 'done'
    return 'pending'


def get_file_details(file_path, file_status):
    """
    Extracts the filename, timestamp, and explanation from a file path and status.

    Args:
        file_path (str): The file path of the upload.
        file_status (str): The status of the upload.

    Returns:
        Tuple[str, int, Optional[str]]: The filename, timestamp, and explanation.
    """
    filename_parts = os.path.basename(file_path).split('_')
    filename = '_'.join(filename_parts[:-2])
    timestamp = int(filename_parts[-2])
    explanation = None
    if file_status == 'done':
        explanation = f"{filename}_output.json"
    return filename, timestamp, explanation


def get_output_file(file_path):
    """
    Retrieves the path of the output file associated with an upload.

    Args:
        file_path (str): The file path of the upload.

    Returns:
        str: The path of the output file if found, or None if not found.
    """
    print(file_path)
    output_filename = f"C:\\Networks\\final-project-AsherMentzer\\outputs\\{os.path.basename(file_path)}.json"
    print(output_filename)
    output_file_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    if os.path.isfile(output_file_path):
        print("found")
        return output_file_path
    return None


def parse_output_file(output_file):
    """
    Parses the content of an output file.

    Args:
        output_file (str): The path of the output file.

    Returns:
        dict: The parsed output data.
    """
    with open(output_file) as file:
        output_data = json.load(file)
    return output_data


def run_web_server():
    """
    Run the Flask web server.
    This function starts the Flask web server to handle incoming requests.
    """
    app.run()


if __name__ == '__main__':
    run_web_server()
