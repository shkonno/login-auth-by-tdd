from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import httpx

from app.domain.jwt import verify_token, create_access_token, create_refresh_token
from app.domain import oauth_config
from app.domain.oauth_service import GoogleOAuthService
from app.domain.user_repository import UserRepository

app = FastAPI(
    title="Auth TDD Learning",
    description="JWT認証をTDDで学ぶプロジェクト",
    version="0.1.0"
)


@app.get("/")
def root():
    return {"message": "Auth API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@app.post("/auth/refresh")
def refresh_access_token(request: RefreshTokenRequest):
    """リフレッシュトークンを使って新しいアクセストークンを取得する"""
    try:
        # リフレッシュトークンを検証
        payload = verify_token(request.refresh_token)
        
        # type: "refresh" であることを確認
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type. Refresh token required."
            )
        
        # 新しいアクセストークンを生成
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload."
            )
        
        new_access_token = create_access_token({"sub": user_id})
        
        return {"access_token": new_access_token}
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        # 期限切れや無効なトークンの場合
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token"
        )


# リポジトリのインスタンス（簡易実装、実際のアプリケーションでは依存性注入を使用）
# テストでモック化可能にするため、グローバル変数として保持
_repository: UserRepository = None


def get_repository() -> UserRepository:
    """リポジトリを取得する（テスト用にモック可能にするため）"""
    global _repository
    if _repository is None:
        # 実際のアプリケーションでは、データベースセッションからリポジトリを作成
        # テストではモック化される
        # ここでは簡易実装として、空のリポジトリを作成
        # 実際のアプリケーションでは、依存性注入を使用すべき
        raise NotImplementedError("Repository must be set before use")
    return _repository


@app.get("/auth/google/callback")
def google_oauth_callback(code: str = Query(None)):
    """Google OAuth認証コールバックエンドポイント
    
    【処理の流れ】
    1. 認証コードを受け取る
    2. Google APIで認証コードをアクセストークンに交換
    3. アクセストークンでユーザー情報を取得
    4. GoogleOAuthServiceでユーザーを作成/取得
    5. JWTトークン（アクセストークン + リフレッシュトークン）を返す
    """
    try:
        # 認証コードの検証
        if not code:
            raise HTTPException(
                status_code=400,
                detail="Authorization code is required"
            )
        
        # Google API設定の確認
        if not oauth_config.GOOGLE_CLIENT_ID or not oauth_config.GOOGLE_CLIENT_SECRET:
            raise HTTPException(
                status_code=500,
                detail="Google OAuth is not configured"
            )
        
        # ステップ1: 認証コードをアクセストークンに交換
        token_data = {
            "code": code,
            "client_id": oauth_config.GOOGLE_CLIENT_ID,
            "client_secret": oauth_config.GOOGLE_CLIENT_SECRET,
            "redirect_uri": oauth_config.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        
        token_response = httpx.post(oauth_config.GOOGLE_TOKEN_URL, data=token_data)
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=401,
                detail="Failed to exchange authorization code for access token"
            )
        
        token_json = token_response.json()
        google_access_token = token_json.get("access_token")
        if not google_access_token:
            raise HTTPException(
                status_code=401,
                detail="Invalid token response from Google"
            )
        
        # ステップ2: アクセストークンでユーザー情報を取得
        headers = {"Authorization": f"Bearer {google_access_token}"}
        userinfo_response = httpx.get(oauth_config.GOOGLE_USERINFO_URL, headers=headers)
        if userinfo_response.status_code != 200:
            raise HTTPException(
                status_code=401,
                detail="Failed to get user information from Google"
            )
        
        google_user_info = userinfo_response.json()
        
        # ステップ3: GoogleOAuthServiceでユーザーを作成/取得
        repository = get_repository()
        oauth_service = GoogleOAuthService(repository)
        user = oauth_service.authenticate(google_user_info)
        
        # ステップ4: JWTトークンを生成
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    except HTTPException:
        raise
    except Exception as e:
        # 予期しないエラーの場合
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
