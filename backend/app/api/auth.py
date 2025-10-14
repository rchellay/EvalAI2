from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.core.security import hash_password, verify_password, create_access_token, get_current_user, decode_token
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=dict)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check existing username/email
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"msg": "Usuario creado correctamente"}

@router.post("/login", response_model=dict)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=dict)
def me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "email": current_user.email}

@router.post("/google", response_model=dict)
def login_google(payload: dict, db: Session = Depends(get_db)):
    """Recibe JSON {"id_token": "..."} y retorna JWT interno."""
    id_token_str = payload.get("id_token")
    if not id_token_str:
        raise HTTPException(status_code=400, detail="Falta id_token")
    try:
        # CLIENT_ID debería estar en variable de entorno; aquí no se valida aud estrictamente para simplificar dev.
        info = id_token.verify_oauth2_token(id_token_str, google_requests.Request())
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        if client_id and info.get("aud") != client_id:
            raise HTTPException(status_code=401, detail="Audiencia no válida")
    except Exception:  # broad for simplicity; refine later
        raise HTTPException(status_code=401, detail="ID token inválido")
    email = info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email no disponible en token")
    username = email.split("@")[0]
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(username=username, email=email, hashed_password=hash_password("oauth_google_placeholder"))
        db.add(user)
        db.commit()
        db.refresh(user)
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
