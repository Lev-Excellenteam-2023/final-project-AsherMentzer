import os
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String, DateTime, create_engine
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker, scoped_session, declarative_base
from typing import List, Optional
from uuid import uuid4

DB_PATH = "db"
DB_NAME = "database.db"
engine = create_engine(rf"sqlite:///{os.path.join(os.path.join(__file__, '..', '..', DB_PATH, DB_NAME))}", echo=True)

# Create a scoped session to manage sessions for each request
Session = scoped_session(sessionmaker(bind=engine))

# Base class for the models
Base = declarative_base()


class UploadStatus:
    done = "done"
    pending = "pending"


def generate_uid() -> str:
    """
    Generates a unique identifier (UID) using the UUID4 algorithm.
    Returns:
        str: The generated unique identifier.
    """
    return str(uuid4())


class User(Base):
    """
    Represents a User entity in the database.
    Attributes:
        id (int): The primary key for the User table.
        email (str): The email address of the user.
        uploads (List[Upload]): A list of uploads associated with the user.
    """
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    uploads: Mapped[List["Upload"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Upload(Base):
    """
    Represents an Upload entity in the database.
    Attributes:
        id (int): The primary key for the Upload table.
        uid (str): The unique identifier for the upload.
        filename (str): The original filename of the uploaded file.
        upload_time (DateTime): The timestamp of when the Web API received the upload.
        finish_time (Optional[DateTime]): The timestamp of when the Explainer finished processing the upload.
        status (str): The current status of the upload (either 'pending' or 'done').
        user_id (Optional[int]): The foreign key referencing the User table,
        indicating the user who uploaded this upload.
    """
    __tablename__ = "Upload"
    id: Mapped[int] = mapped_column(primary_key=True)
    uid: Mapped[str] = mapped_column(String(36), default=generate_uid, nullable=False, unique=True)
    filename: Mapped[str] = mapped_column(String(128), nullable=False)
    upload_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    finish_time: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    status: Mapped[UploadStatus] = mapped_column(Enum(UploadStatus.pending, UploadStatus.done),
                                                 default=UploadStatus.pending)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('user.id'))
    user: Mapped["User"] = relationship(back_populates="uploads")

    def __repr__(self) -> str:
        return f"Upload(id={self.id!r}, uid={self.uid!r}), filename={self.filename!r}), " \
               f"upload_time={self.upload_time!r}), status={self.status!r}), user_id={self.user_id!r})"

    def upload_path(self, base_path="."):
        """Computes the path of the uploaded file based on metadata in the DB.
        :param base_path: The base directory where the file will be stored. Default is the current directory.
        :return: The computed path for the uploaded file.
        """
        return os.path.join(base_path, f"{self.uid}.{self.filename.split('.')[-1]}")


def create_all():
    """
    Creates all the tables defined in the models.
    This function should be called when setting up the application to create the necessary tables in the database.
    """
    Base.metadata.create_all(engine)


def save_upload(file):
    """
    Saves the uploaded file as an anonymous upload.
    This function creates an Upload object in the database to represent the uploaded file
    and saves the file to the uploads folder using a generated UID. The function returns
    the UID associated with the uploaded file.
    Args:
        file (FileStorage): The uploaded file to be saved.
    Returns:
        str: The UID associated with the uploaded file.
    """
    with Session() as session:
        anonymous_upload = Upload(filename=file.filename, upload_time=datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
        session.add(anonymous_upload)
        session.commit()
        _, file_type = os.path.splitext(file.filename)
        file.save(os.path.join('uploads', f"{anonymous_upload.uid}{file_type}"))
        return anonymous_upload.uid


def save_upload_with_email(file, email: str):
    """
    Saves the uploaded file with the associated user.
    This function creates a User object in the database if the user with the provided
    email doesn't exist. It then creates an Upload object associated with the user and
    saves the file to the uploads folder using a generated UID. The function returns
    the UID associated with the uploaded file.
    Args:
        file (FileStorage): The uploaded file to be saved.
        email (str): The email of the user associated with the uploaded file.
    Returns:
        str: The UID associated with the uploaded file.
    """
    with Session() as session:
        user = session.query(User).filter_by(email=email).first()
        if not user:
            user = User(email=email)
            session.add(user)
            session.commit()
        user_upload = Upload(filename=file.filename, upload_time=datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
                             user=user)
        session.add(user_upload)
        session.commit()
        _, file_type = os.path.splitext(file.filename)
        file.save(os.path.join("uploads", f"{user_upload.uid}{file_type}"))
        return user_upload.uid


def save_to_json(uid: str, upload_status: str, name: str, finish_time: datetime = None, explanation=None):
    """
    Creates a dictionary object to represent the upload status, including the
    filename, timestamp, processing status, and an optional explanation.
    Args:
        uid: the uid of the upload.
        upload_status: The status of the upload.
        name: The name of the file.
        finish_time: ThAn optional finish time of the upload.
        explanation: An optional explanation for the upload status.
    Returns:
        Dict: A dictionary representing the upload status.
    """
    return {
        'uid': uid,
        'status': upload_status,
        'filename': name,
        'finish time': str(finish_time),
        'explanation': explanation
    }


def get_engine():
    return engine


def create_all_tables():
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    create_all_tables()