"""JWT生成・検証機能のテスト"""

from datetime import timedelta

import jwt
import pytest

from app.domain.jwt import create_access_token, verify_token, SECRET_KEY, ALGORITHM


class TestCreateAccessToken:
    """JWTトークン生成のテスト"""

    def test_トークンが文字列で返される(self):
        """create_access_tokenは文字列のトークンを返す"""
        data = {"sub": "user@example.com"}

        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_有効期限付きトークンにexpクレームが含まれる(self):
        """expires_deltaを指定するとトークンにexpが含まれる"""
        data = {"sub": "user@example.com"}
        expires = timedelta(minutes=30)

        token = create_access_token(data, expires_delta=expires)

        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in decoded


class TestVerifyToken:
    """JWTトークン検証のテスト"""

    def test_有効なトークンをデコードできる(self):
        """verify_tokenは有効なトークンのペイロードを返す"""
        data = {"sub": "user@example.com"}
        token = create_access_token(data)

        payload = verify_token(token)

        assert payload["sub"] == "user@example.com"

    def test_不正なトークンで例外が発生する(self):
        """無効なトークンはエラーになる"""
        invalid_token = "invalid.token.here"

        with pytest.raises(jwt.InvalidTokenError):
            verify_token(invalid_token)

    def test_期限切れトークンで例外が発生する(self):
        """期限切れのトークンはエラーになる"""
        data = {"sub": "user@example.com"}
        expires = timedelta(seconds=-1)  # 1秒前に期限切れ

        token = create_access_token(data, expires_delta=expires)

        with pytest.raises(Exception):
            verify_token(token)
