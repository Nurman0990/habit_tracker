from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from schemas import User
from auth import (
    register_user,
    login_user,
    get_current_user
)


router = APIRouter(
    tags=["Auth"]
)


@router.post("/register")
def register(
    user: User,
    db=Depends(get_db)
):
    new_user = register_user(
        user,
        db
    )

    return {
        "message": "User registered successfully",
        "username": new_user.username
    }


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db=Depends(get_db)
):
    token = login_user(
        form_data,
        db
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me")
def get_me(
    user=Depends(get_current_user)
):
    return {
        "user_id": user["user_id"],
        "username": user["username"]
    }
