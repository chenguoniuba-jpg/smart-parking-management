from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import backend.database
from backend.database import Admin
from backend.schemas import TokenData
from backend.config import SECRET_KEY
from backend.security import hash_password as secure_hash_password
from backend.security import verify_password as secure_verify_password

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return secure_verify_password(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return secure_hash_password(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_admin(db: Session, username: str, password: str) -> Optional[Admin]:
    admin = db.query(Admin).filter(Admin.username == username).first()
    if not admin:
        return None
    if not admin.verify_password(password):
        return None
    return admin

async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(backend.database.get_db)
) -> Admin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        admin_id: int = payload.get("admin_id")
        if username is None or admin_id is None:
            raise credentials_exception
        token_data = TokenData(username=username, admin_id=admin_id)
    except JWTError:
        raise credentials_exception
    
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if admin is None:
        raise credentials_exception
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理员账户已被禁用"
        )
    
    return admin

async def get_current_active_admin(
    current_admin: Admin = Depends(get_current_admin)
) -> Admin:
    if not current_admin.is_active:
        raise HTTPException(status_code=400, detail="管理员账户已被禁用")
    return current_admin

async def get_current_superuser(
    current_admin: Admin = Depends(get_current_admin)
) -> Admin:
    if not current_admin.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要超级管理员权限"
        )
    return current_admin
