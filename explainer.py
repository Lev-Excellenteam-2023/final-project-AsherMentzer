import os
import time
import json
import asyncio
from datetime import datetime
from presentation_parser import PresentationParser
from gpt_slide_explainer import GPTSlideExpander
from db.db_engine import Upload, UploadStatus, get_engine
from sqlalchemy.orm import Session

UPLOADS_FOLDER = 'uploads'
OUTPUTS_FOLDER = 'outputs'
STATUS_FILE = 'status.json'
SLEEP_TIME = 10  # seconds


def process_files():
    """
    Continuously processes unprocessed files.

    The function scans the uploads folder for unprocessed files and processes each file one by one.
    After processing, it saves the explanation, updates the status, and sleeps for a specified duration.
    """
    while True:
        engine = get_engine()
        with Session(engine) as session:
            pending_status = UploadStatus.pending
            upload_files = session.query(Upload).filter_by(status=pending_status).all()
            for upload_file in upload_files:
                try:
                    upload_path = f"{UPLOADS_FOLDER}/{upload_file.filename}"
                    presentation = load_presentation(upload_path)
                    explanation = generate_explanation(presentation)
                    upload_file.finish_time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                    upload_file.status = UploadStatus.done
                    output_file = save_explanation(explanation, upload_path)
                    print(f"Saved explanation to: {output_file}")
                    session.commit()
                except KeyError:
                    continue
        # unprocessed_files = find_unprocessed_files()
        #
        # for file_path in unprocessed_files:
        #     print(f"Processing file: {file_path}")
        #
        #     presentation = load_presentation(file_path)
        #     explanation = generate_explanation(presentation)
        #
        #     output_file = save_explanation(explanation, file_path)
        #     print(f"Saved explanation to: {output_file}")
        #
        #     update_status(file_path)

        time.sleep(SLEEP_TIME)


def find_unprocessed_files():
    """
    Finds unprocessed files in the uploads folder.

    Returns:
        List[str]: List of file paths of unprocessed files.
    """
    status = load_status()
    processed_files = set(status.keys())
    unprocessed_files = []

    for file_name in os.listdir(UPLOADS_FOLDER):
        if file_name not in processed_files:
            unprocessed_files.append(os.path.join(UPLOADS_FOLDER, file_name))

    return unprocessed_files


def load_status():
    """
    Loads the status file.

    Returns:
        dict: Dictionary containing the status information.
    """
    if not os.path.exists(STATUS_FILE):
        return {}

    with open(STATUS_FILE) as f:
        status = json.load(f)

    return status


def update_status(file_path):
    """
    Updates the status file with the processed file.

    Args:
        file_path (str): The path of the processed file.
    """
    status = load_status()
    file_name = os.path.basename(file_path)
    status[file_name] = int(time.time())

    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f)


def load_presentation(file_path):
    """
    Loads a PowerPoint presentation from a file.

    Args:
        file_path (str): The path of the PowerPoint presentation file.

    Returns:
        Presentation_parser: The loaded presentation parsed object.
    """
    presentation = PresentationParser(file_path)
    presentation.parse()
    return presentation


def generate_explanation(presentation, main_topic: str = None):
    """
    Generates an explanation for a PowerPoint presentation.

    Args:
        main_topic: (Str): The topic of this presentation.
        presentation (Presentation_parser): The presentation object to generate the explanation for.

    Returns:
        dict: The generated explanation.
    """
    explainer = GPTSlideExpander()
    if not main_topic:
        main_topic = asyncio.run(explainer.generate_topic_for_presentation(
            presentation.get_all_presentation_text()))
    asyncio.run(
        GPTSlideExpander.generate_explanation_for_presentation(explainer, presentation.presentation_text,
                                                               main_topic)
    )
    return explainer.expanded_slide_explanations


def save_explanation(explanation, file_path):
    """
    Saves the explanation to a file.

    Args:
        explanation (dict): The explanation to be saved.
        file_path (str): The path of the original file.

    Returns:
        str: The path of the saved explanation file.
    """
    file_name = os.path.basename(file_path)
    output_file = os.path.join(OUTPUTS_FOLDER, f"{file_name}.json")

    with open(output_file, 'w') as f:
        json.dump(explanation, f)

    return output_file


if __name__ == '__main__':
    process_files()
