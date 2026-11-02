from pydantic import BaseModel


class Habit(BaseModel):
    name: str
    description: str | None = None


class User(BaseModel):
    username: str
    password: str

