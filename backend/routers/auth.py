from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import backend.database
from backend.database import Admin
from backend.schemas import AdminCreate, AdminResponse, AdminLogin, PasswordChange, Token
from backend.auth import (
    authenticate_admin,
    create_access_token,
    get_current_active_admin,
    get_current_superuser,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
def register_admin(
    admin: AdminCreate,
    db: Session = Depends(backend.database.get_db),
    current_admin: Admin = Depends(get_current_superuser),
):
    existing_admin = db.query(Admin).filter(Admin.username == admin.username).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    existing_email = db.query(Admin).filter(Admin.email == admin.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    new_admin = Admin(
        username=admin.username,
        email=admin.email,
        is_superuser=admin.is_superuser
    )
    new_admin.set_password(admin.password)
    
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    
    return new_admin

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(backend.database.get_db)
):
    admin = authenticate_admin(db, form_data.username, form_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.username, "admin_id": admin.id},
        expires_delta=access_token_expires
    )
    
    from datetime import datetime
    admin.last_login = datetime.utcnow()
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login/json", response_model=Token)
def login_json(login_data: AdminLogin, db: Session = Depends(backend.database.get_db)):
    admin = authenticate_admin(db, login_data.username, login_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.username, "admin_id": admin.id},
        expires_delta=access_token_expires
    )
    
    from datetime import datetime
    admin.last_login = datetime.utcnow()
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=AdminResponse)
def get_current_admin_info(current_admin: Admin = Depends(get_current_active_admin)):
    return current_admin

@router.get("/admins", response_model=list[AdminResponse])
def list_admins(
    skip: int = 0,
    limit: int = 100,
    current_admin: Admin = Depends(get_current_superuser),
    db: Session = Depends(backend.database.get_db),
):
    admins = db.query(Admin).offset(skip).limit(limit).all()
    return admins

@router.delete("/admins/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin(
    admin_id: int,
    current_admin: Admin = Depends(get_current_superuser),
    db: Session = Depends(backend.database.get_db),
):
    if admin_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账户"
        )
    
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="管理员不存在"
        )
    
    db.delete(admin)
    db.commit()
    return None

@router.put("/admins/{admin_id}/status")
def update_admin_status(
    admin_id: int,
    is_active: bool,
    current_admin: Admin = Depends(get_current_superuser),
    db: Session = Depends(backend.database.get_db),
):
    if admin_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的账户状态"
        )
    
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="管理员不存在"
        )
    
    admin.is_active = is_active
    db.commit()
    db.refresh(admin)
    
    return {"message": "状态更新成功", "is_active": is_active}

@router.put("/change-password")
def change_password(
    password_change: PasswordChange,
    current_admin: Admin = Depends(get_current_active_admin),
    db: Session = Depends(backend.database.get_db),
):
    if not current_admin.verify_password(password_change.old_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )
    
    current_admin.set_password(password_change.new_password)
    db.commit()
    
    return {"message": "密码修改成功"}
