from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from pymongo.database import Database
from typing import Annotated
from utils.security import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    verify_password
)
from config import settings
from models.user_model import UserCreate, UserInDB

router = APIRouter()


# TEST KULLANICISI OLUŞTURMA (Sadece geliştirme ortamında)
async def create_test_user(db: Database):
    test_username = "testuser@example.com"
    test_password = "Test1234!"

    if not db.users.find_one({"username": test_username}):
        test_user = {
            "username": test_username,
            "email": test_username,
            "hashed_password": get_password_hash(test_password),
            "disabled": False,
            "fullname": "Test Kullanıcı"
        }
        db.users.insert_one(test_user)
        print("\n" + "=" * 50)
        print("🔥 TEST KULLANICISI OLUŞTURULDU")
        print(f"👤 Kullanıcı Adı: {test_username}")
        print(f"🔑 Şifre: {test_password}")
        print("=" * 50 + "\n")


# KAYIT OLMA ENDPOINTİ
@router.post("/register")
async def register(user: UserCreate, db: Database = Depends(get_db)):
    # Kullanıcı var mı kontrol et
    existing_user = db.users.find_one({
        "$or": [
            {"username": user.username},
            {"email": user.email}
        ]
    })

    if existing_user:
        if existing_user["username"] == user.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu kullanıcı adı zaten kayıtlı"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu e-posta adresi zaten kayıtlı"
            )

    # Şifreyi hashle
    hashed_password = get_password_hash(user.password)

    # Kullanıcıyı veritabanına kaydet
    user_data = {
        "username": user.username,
        "email": user.email,
        "fullname": user.fullname,
        "hashed_password": hashed_password,
        "disabled": False,
        "created_at": datetime.utcnow()
    }

    db.users.insert_one(user_data)

    return {
        "message": "Kullanıcı başarıyla oluşturuldu",
        "username": user.username
    }


# GİRİŞ YAPMA ENDPOINTİ
@router.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Database = Depends(get_db)
):
    # Test kullanıcısını oluştur (sadece geliştirme ortamında)
    await create_test_user(db)

    # Kullanıcıyı doğrula
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Token oluştur
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user["username"],
        "fullname": user.get("fullname", "")
    }


# KULLANICI BİLGİLERİ ENDPOINTİ
@router.get("/me")
async def read_users_me(
        current_user: UserInDB = Depends(get_current_active_user)
):
    return {
        "username": current_user.username,
        "email": current_user.email,
        "fullname": getattr(current_user, "fullname", ""),
        "disabled": current_user.disabled
    }


# BAĞIMLILIKLER
def get_db():
    from app import db
    return db


def get_current_active_user():
    from utils.security import get_current_active_user
    return get_current_active_user