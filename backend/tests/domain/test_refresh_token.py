"""リフレッシュトークン生成機能のテスト"""

from datetime import timedelta

import jwt
import pytest

from app.domain.jwt import create_refresh_token, verify_token, SECRET_KEY, ALGORITHM


class TestCreateRefreshToken:
    """リフレッシュトークン生成のテスト"""

    def test_リフレッシュトークンが文字列で返される(self):
        """create_refresh_tokenは文字列のトークンを返す"""
        data = {"sub": "user@example.com"}

        token = create_refresh_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_リフレッシュトークンに長い有効期限が設定されている(self):
        """リフレッシュトークンはデフォルトで7日間の有効期限を持つ"""
        data = {"sub": "user@example.com"}

        token = create_refresh_token(data)

        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in decoded
        # 有効期限が7日間（約604800秒）であることを確認
        # 実際のexpは現在時刻+7日なので、exp - iat が約7日間であることを確認
        if "iat" in decoded:
            exp_delta = decoded["exp"] - decoded["iat"]
            assert exp_delta >= 604800 - 60  # 60秒の誤差を許容
            assert exp_delta <= 604800 + 60

    def test_リフレッシュトークンに適切なペイロードが含まれている(self):
        """リフレッシュトークンにはsubとtypeが含まれる"""
        data = {"sub": "user@example.com"}

        token = create_refresh_token(data)

        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "user@example.com"
        assert decoded["type"] == "refresh"

    def test_リフレッシュトークンを検証できる(self):
        """verify_tokenでリフレッシュトークンを検証できる"""
        data = {"sub": "user@example.com"}
        token = create_refresh_token(data)

        payload = verify_token(token)

        assert payload["sub"] == "user@example.com"
        assert payload["type"] == "refresh"

    def test_カスタム有効期限を指定できる(self):
        """expires_deltaを指定するとカスタム有効期限を設定できる"""
        data = {"sub": "user@example.com"}
        expires = timedelta(days=14)

        token = create_refresh_token(data, expires_delta=expires)

        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in decoded
        if "iat" in decoded:
            exp_delta = decoded["exp"] - decoded["iat"]
            assert exp_delta >= 1209600 - 60  # 14日間（秒）- 60秒の誤差を許容
            assert exp_delta <= 1209600 + 60

