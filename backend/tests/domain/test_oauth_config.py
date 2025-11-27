"""Google OAuth設定のテスト"""

import os
import pytest
from unittest.mock import patch

from app.domain.oauth_config import (
    is_google_oauth_configured,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
    GOOGLE_AUTHORIZATION_BASE_URL,
    GOOGLE_TOKEN_URL,
    GOOGLE_USERINFO_URL,
    GOOGLE_SCOPES
)


def test_oauth設定の定数が定義されている():
    """OAuth設定の定数が正しく定義されている"""
    assert GOOGLE_AUTHORIZATION_BASE_URL == "https://accounts.google.com/o/oauth2/v2/auth"
    assert GOOGLE_TOKEN_URL == "https://oauth2.googleapis.com/token"
    assert GOOGLE_USERINFO_URL == "https://www.googleapis.com/oauth2/v2/userinfo"
    assert isinstance(GOOGLE_SCOPES, list)
    assert len(GOOGLE_SCOPES) > 0


def test_リダイレクトURIがデフォルト値を持つ():
    """リダイレクトURIがデフォルト値を持つ"""
    assert GOOGLE_REDIRECT_URI is not None
    assert isinstance(GOOGLE_REDIRECT_URI, str)


@patch.dict(os.environ, {
    "GOOGLE_CLIENT_ID": "test-client-id",
    "GOOGLE_CLIENT_SECRET": "test-client-secret"
}, clear=False)
def test_環境変数が設定されている場合に設定完了と判定される():
    """環境変数が設定されている場合、設定完了と判定される"""
    # モジュールを再インポートして環境変数を読み込む
    import importlib
    import app.domain.oauth_config
    importlib.reload(app.domain.oauth_config)
    
    assert app.domain.oauth_config.is_google_oauth_configured() is True


@patch.dict(os.environ, {
    "GOOGLE_CLIENT_ID": "",
    "GOOGLE_CLIENT_SECRET": ""
}, clear=False)
def test_環境変数が空文字列の場合に設定未完了と判定される():
    """環境変数が空文字列の場合、設定未完了と判定される"""
    import importlib
    import app.domain.oauth_config
    importlib.reload(app.domain.oauth_config)
    
    assert app.domain.oauth_config.is_google_oauth_configured() is False


@patch.dict(os.environ, {}, clear=True)
def test_環境変数が設定されていない場合に設定未完了と判定される():
    """環境変数が設定されていない場合、設定未完了と判定される"""
    import importlib
    import app.domain.oauth_config
    importlib.reload(app.domain.oauth_config)
    
    assert app.domain.oauth_config.is_google_oauth_configured() is False

