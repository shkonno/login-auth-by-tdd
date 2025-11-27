from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from app.domain.registration_service import RegistrationService
from app.domain.login_service import LoginService
from app.domain.jwt import verify_token
from app.infrastructure.user_repository import SqlAlchemyUserRepository
from app.infrastructure.database import SessionLocal

app = FastAPI(
    title="Auth TDD Learning",
    description="JWT認証をTDDで学ぶプロジェクト",
    version="0.1.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # フロントエンドのURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserRegistrationRequest(BaseModel):
    email: EmailStr
    password: str


class UserRegistrationResponse(BaseModel):
    id: str
    email: str


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    access_token: str


class CurrentUserResponse(BaseModel):
    id: str
    email: str


@app.get("/")
def root():
    return {"message": "Auth API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/api/register", status_code=201, response_model=UserRegistrationResponse)
def register_user(request: UserRegistrationRequest):
    # パスワードの長さをチェック
    if len(request.password) < 8:
        raise HTTPException(status_code=400, detail={"error": "Password must be at least 8 characters long"})

    try:
        # データベースセッション作成
        db = SessionLocal()
        try:
            repository = SqlAlchemyUserRepository(db)
            service = RegistrationService(repository)

            # ユーザー登録
            user = service.register(request.email, request.password)

            return UserRegistrationResponse(
                id=str(user.id),
                email=user.email
            )
        finally:
            db.close()

    except ValueError as e:
        # 重複メールアドレスエラー
        raise HTTPException(status_code=409, detail={"error": str(e)})
    except Exception as e:
        # その他のエラー
        raise HTTPException(status_code=400, detail={"error": str(e)})


@app.post("/api/login", status_code=200, response_model=UserLoginResponse)
def login_user(request: UserLoginRequest):
    try:
        # データベースセッション作成
        db = SessionLocal()
        try:
            repository = SqlAlchemyUserRepository(db)
            service = LoginService(repository)

            # ログイン処理
            token = service.login(request.email, request.password)

            return UserLoginResponse(
                access_token=token
            )
        finally:
            db.close()

    except ValueError as e:
        # 認証エラー（メールアドレスまたはパスワードが間違っている）
        raise HTTPException(status_code=401, detail={"error": "Invalid email or password"})
    except Exception as e:
        # その他のエラー
        raise HTTPException(status_code=400, detail={"error": str(e)})


def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """Authorizationヘッダーからトークンを取得して検証し、ユーザーIDを返す"""
    if not authorization:
        raise HTTPException(status_code=401, detail={"error": "Authorization header is missing"})
    
    # "Bearer {token}" の形式からトークンを抽出
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail={"error": "Invalid authorization header format"})
    
    token = parts[1]
    
    try:
        # トークンを検証
        payload = verify_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail={"error": "Invalid token payload"})
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail={"error": "Invalid or expired token"})


@app.get("/api/users/me", response_model=CurrentUserResponse)
def get_current_user(user_id: str = Depends(get_current_user_id)):
    """現在ログインしているユーザーの情報を取得"""
    try:
        # データベースセッション作成
        db = SessionLocal()
        try:
            repository = SqlAlchemyUserRepository(db)
            
            # ユーザーIDでユーザーを検索
            user = repository.find_by_id(UUID(user_id))
            if not user:
                raise HTTPException(status_code=404, detail={"error": "User not found"})
            
            return CurrentUserResponse(
                id=str(user.id),
                email=user.email
            )
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})
