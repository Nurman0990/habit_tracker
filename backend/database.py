import os
from dotenv import load_dotenv

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Date,
    Boolean,
    ForeignKey
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


Base = declarative_base()


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(
        String,
        unique=True,
        nullable=False
    )

    password = Column(
        String,
        nullable=False
    )

    habits = relationship(
        "HabitDB",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class HabitDB(Base):
    __tablename__ = "habits"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
        nullable=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    user = relationship(
        "UserDB",
        back_populates="habits"
    )

    completions = relationship(
        "HabitCompletionDB",
        back_populates="habit",
        cascade="all, delete-orphan"
    )


class HabitCompletionDB(Base):
    __tablename__ = "habit_completions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    habit_id = Column(
        Integer,
        ForeignKey("habits.id"),
        nullable=False
    )

    date = Column(
        Date,
        nullable=False
    )

    completed = Column(
        Boolean,
        default=True
    )

    habit = relationship(
        "HabitDB",
        back_populates="completions"
    )
