"""Google OAuth設定

【なぜこのファイルが必要？】
Google OAuth認証に必要な設定を一元管理するため。

【設定項目】
- Google OAuth Client ID
- Google OAuth Client Secret
- リダイレクトURI
- スコープ（取得する情報の範囲）
"""

import os
from typing import Optional

# Google OAuth設定
# 環境変数から読み込む（本番環境では.envファイルから）
GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI: Optional[str] = os.getenv(
    "GOOGLE_REDIRECT_URI",
    "http://localhost:3000/auth/google/callback"
)

# OAuth認証サーバーのURL
GOOGLE_AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# リクエストするスコープ（ユーザー情報とメールアドレス）
GOOGLE_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]


def is_google_oauth_configured() -> bool:
    """Google OAuth設定が完了しているか確認する"""
    return (
        GOOGLE_CLIENT_ID is not None
        and GOOGLE_CLIENT_SECRET is not None
        and GOOGLE_CLIENT_ID != ""
        and GOOGLE_CLIENT_SECRET != ""
    )

