from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import UserCreate, UserOut, UserLogin, Token
from crud import create_user, authenticate_user, get_user_by_email, get_user_by_username, search_users
from auth import create_access_token
from dependencies import get_current_user
from models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    if get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    return create_user(db, user_data)


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/search", response_model=list[UserOut])
def search(keyword: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return search_users(db, keyword, current_user.id)
