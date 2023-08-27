from datetime import datetime
import os
import json
import uuid
from typing import Dict, Union

from sqlalchemy import select
from sqlalchemy.orm import Session
from db.db_engine import Upload, User, UploadStatus, save_to_json, get_engine
from flask import Flask, request, jsonify, Response, redirect, url_for, flash

from explainer import OUTPUTS_FOLDER

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
    email = request.form.get('email')
    engine = get_engine()
    with Session(engine) as session:
        f_upload = Upload(uid=uid, filename=os.path.basename(file.filename),
                          upload_time=datetime.now(), status='pending')
        new_filename = f_upload.upload_path(app.config['UPLOAD_FOLDER'])
        session.add(f_upload)
        session.commit()

        if email:
            user = _get_user_by_email(email, session)
            if not user:
                user = User(email=email)
            user.uploads.append(f_upload)
            f_upload.user = user
            f_upload.user_id = user.id
            session.add_all([user, f_upload])
            session.commit()

    file.save(new_filename)
    return jsonify({'uid': str(uid)})

    # filename = get_filename(file.filename)
    # timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')  # int(time.time())
    # email = request.form.get('email')
    # if email:
    #     uid = save_upload_with_email(file, email)
    # else:
    #     new_filename = f"{filename}_{timestamp}_{uid}"
    #     file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
    #     file.save(file_path)
    # response = {'uid': uid}
    # return jsonify(response)


@app.route('/status/<uid>', methods=['GET'])
def status(uid):
    """
    API endpoint for checking the status of an upload.

    Args:
        uid (str): The UID of the upload.

    Returns:
        flask.Response: JSON response containing the status, filename, timestamp, and explanation of the upload.
    """
    email = None
    filename = None
    print(uid)
    if '@' in uid:
        filename, email = uid.split(' ')
        uid = None
    # email = request.form.get('email')
    # filename = request.form.get('filename')
    if uid:
        response = get_status_by_uid(uid)
        if not response:
            return jsonify({'status': 'not found'}), 404
    elif email and filename:  # Only search if both
        get_status_by_email_and_filename(email, filename)
    else:
        flash("Please enter a UID, or provide both email and filename")


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


def get_output_path(filename: str) -> str:
    """
    Retrieves the path to the output file associated with the given filename.
    Args:
        filename (str): The filename for which to retrieve the output path.
    Returns:
        str: The path to the output file.
    """
    name, _ = os.path.splitext(filename)
    return os.path.join(OUTPUTS_FOLDER, f"{name}.json")


def load_output(filename: str) -> Dict:
    """
    Loads the content of the output file associated with the given filename as a JSON object.
    Args:
        filename (str): The filename of the output file to be loaded.
    Returns:
        Dict: The loaded JSON content as a dictionary.
    """
    output_path = get_output_path(filename)
    with open(output_path, 'r') as file:
        return json.load(file)


def get_status_by_uid(uid):
    engine = get_engine()
    with Session(engine) as session:
        file_data = session.query(Upload).filter_by(uid=uid).first()
        if file_data:
            if file_data.status == UploadStatus.done:
                output = load_output(f"{uid}.json")
                status_info = save_to_json(uid, file_data.status, file_data.filename, file_data.finish_time, output)
            else:
                status_info = save_to_json(uid, file_data.status, file_data.filename, file_data.finish_time)
            return Response(json.dumps(status_info), mimetype='application/json')
        else:
            return None


def get_status_by_email_and_filename(email, filename):
    engine = get_engine()
    with Session(engine) as session:
        user = session.query(User).filter_by(email=email).first()
        if user:
            latest_upload = session.query(Upload).filter_by(user=user, filename=filename).order_by(
                Upload.upload_time.desc()).first()
            if latest_upload:
                return redirect(url_for('status', uid=latest_upload.uid))
            else:
                flash("Filename not found")
        else:
            flash(f"Email: {email} does not exist")


def _get_user_by_email(email, session: Session) -> Union[User, None]:
    """
    Retrieves a user by their email address.
    :param email: The email address of the user to be retrieved.
    :param session: The SQLAlchemy session object.
    :return: User or None - The User object if found, or None if the user does not exist.
    """
    select_statement = select(User).where(User.email == email)
    result = session.scalars(select_statement).all()
    if result:
        return result[0]
    else:
        return None


if __name__ == '__main__':
    run_web_server()
