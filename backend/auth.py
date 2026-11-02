import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from database import UserDB
from datetime import datetime, timedelta, timezone

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def get_current_user(
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


def register_user(user, db):
    existing_user = (
        db.query(UserDB)
        .filter(
            UserDB.username == user.username
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )

    hashed_password = pwd_context.hash(
        user.password
    )

    new_user = UserDB(
        username=user.username,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def login_user(form_data, db):
    existing_user = (
        db.query(UserDB)
        .filter(
            UserDB.username == form_data.username
        )
        .first()
    )

    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    password_correct = pwd_context.verify(
        form_data.password,
        existing_user.password
    )

    if not password_correct:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token_data = {
    "user_id": existing_user.id,
    "username": existing_user.username,
    "exp": datetime.now(timezone.utc) + timedelta(days=7)
}

    token = jwt.encode(
        token_data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token
