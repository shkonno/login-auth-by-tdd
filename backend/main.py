from fastapi import FastAPI, HTTPException, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
import httpx
from app.domain.registration_service import RegistrationService
from app.domain.login_service import LoginService
from app.domain.jwt import verify_token, create_access_token, create_refresh_token
from app.domain.oauth_service import GoogleOAuthService
from app.domain import oauth_config
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


class OAuthCallbackResponse(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str


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


@app.get("/auth/google/callback", response_model=OAuthCallbackResponse)
def google_oauth_callback(code: Optional[str] = Query(None)):
    """Google OAuth認証コールバックエンドポイント
    
    認証コードを受け取り、Google APIでトークン交換とユーザー情報取得を行い、
    JWTトークンを返す。
    """
    # 認証コードのチェック
    if not code:
        raise HTTPException(status_code=400, detail={"error": "Authorization code is required"})
    
    try:
        # データベースセッション作成
        db = SessionLocal()
        try:
            repository = SqlAlchemyUserRepository(db)
            oauth_service = GoogleOAuthService(repository)
            
            # Google OAuth設定の確認
            if not oauth_config.is_google_oauth_configured():
                raise HTTPException(status_code=500, detail={"error": "Google OAuth is not configured"})
            
            # ステップ1: 認証コードをアクセストークンに交換
            token_response = httpx.post(
                oauth_config.GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": oauth_config.GOOGLE_CLIENT_ID,
                    "client_secret": oauth_config.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": oauth_config.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code"
                }
            )
            
            if token_response.status_code != 200:
                error_data = token_response.json() if token_response.headers.get("content-type", "").startswith("application/json") else {}
                raise HTTPException(status_code=401, detail={"error": error_data.get("error", "Failed to exchange authorization code")})
            
            token_data = token_response.json()
            google_access_token = token_data.get("access_token")
            
            if not google_access_token:
                raise HTTPException(status_code=401, detail={"error": "Failed to get access token from Google"})
            
            # ステップ2: Google APIでユーザー情報を取得
            userinfo_response = httpx.get(
                oauth_config.GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {google_access_token}"}
            )
            
            if userinfo_response.status_code != 200:
                raise HTTPException(status_code=500, detail={"error": "Failed to get user info from Google"})
            
            google_user_info = userinfo_response.json()
            
            # ステップ3: GoogleOAuthServiceでユーザーを作成または取得
            user = oauth_service.authenticate(google_user_info)
            
            # ステップ4: JWTトークンを生成
            access_token = create_access_token({"sub": str(user.id)})
            refresh_token = create_refresh_token({"sub": str(user.id)})
            
            return OAuthCallbackResponse(
                access_token=access_token,
                refresh_token=refresh_token
            )
        finally:
            db.close()
    
    except HTTPException:
        raise
    except Exception as e:
        # Google API呼び出し失敗などの予期しないエラー
        raise HTTPException(status_code=500, detail={"error": str(e)})


@app.post("/auth/refresh", response_model=RefreshTokenResponse)
def refresh_access_token(request: RefreshTokenRequest):
    """リフレッシュトークンでアクセストークンを更新するエンドポイント
    
    有効なリフレッシュトークンを受け取り、新しいアクセストークンを返す。
    """
    refresh_token = request.refresh_token
    
    try:
        # ステップ1: リフレッシュトークンを検証
        payload = verify_token(refresh_token)
        
        # ステップ2: トークンのtypeが"refresh"であることを確認
        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(status_code=401, detail={"error": "Invalid token type. Refresh token required."})
        
        # ステップ3: ユーザーIDを取得
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail={"error": "Invalid token payload"})
        
        # ステップ4: 新しいアクセストークンを生成
        access_token = create_access_token({"sub": user_id})
        
        return RefreshTokenResponse(access_token=access_token)
    
    except HTTPException:
        raise
    except Exception as e:
        # トークン検証エラー（期限切れ、無効なトークンなど）
        raise HTTPException(status_code=401, detail={"error": "Invalid or expired refresh token"})
