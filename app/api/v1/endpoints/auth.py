from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.api import deps
from app.core import security
from app.models.user import User, UserCreate, UserRead
from app.db.session import get_session

router = APIRouter()

@router.post("/register", response_model=UserRead)
def register_user(user_in: UserCreate, db: Session = Depends(get_session)):
    statement = select(User).where(User.email == user_in.email)
    existing_user = db.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="The user with this email already exists")
    
    statement = select(User).where(User.username == user_in.username)
    existing_user = db.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="The user with this username already exists")
    
    hashed_password = security.get_password_hash(user_in.password)
    user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login")
def login(db: Session = Depends(get_session), form_data: OAuth2PasswordRequestForm = Depends()):
    statement = select(User).where(User.username == form_data.username)
    user = db.exec(statement).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = security.create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}
