"""JWT生成・検証機能のテスト"""

import os
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


class TestJWTConfig:
    """JWT設定の環境変数読み込みテスト"""

    def test_環境変数からSECRET_KEYを読み込む(self):
        """環境変数JWT_SECRET_KEYが設定されている場合、その値が使用される"""
        # 環境変数を設定
        test_secret = "test-secret-key-from-env"
        os.environ["JWT_SECRET_KEY"] = test_secret
        
        # jwtモジュールを再インポートして環境変数を読み込ませる
        import importlib
        import app.domain.jwt as jwt_module
        importlib.reload(jwt_module)
        
        # 環境変数から読み込んだ値が使用されていることを確認
        assert jwt_module.SECRET_KEY == test_secret
        
        # クリーンアップ
        del os.environ["JWT_SECRET_KEY"]
        importlib.reload(jwt_module)

    def test_環境変数が設定されていない場合デフォルト値が使用される(self):
        """環境変数JWT_SECRET_KEYが設定されていない場合、デフォルト値が使用される"""
        import importlib
        import app.domain.jwt as jwt_module
        
        # 環境変数を削除（もし設定されていれば）
        original_value = os.environ.pop("JWT_SECRET_KEY", None)
        
        # jwtモジュールを再インポートして環境変数を読み込ませる
        importlib.reload(jwt_module)
        
        # デフォルト値が使用されていることを確認
        assert jwt_module.SECRET_KEY == "your-secret-key-here"
        
        # クリーンアップ：元の値を復元（もし存在していたら）
        if original_value is not None:
            os.environ["JWT_SECRET_KEY"] = original_value
            importlib.reload(jwt_module)

    def test_環境変数設定時に既存のJWT機能が正常に動作する(self):
        """環境変数JWT_SECRET_KEYが設定されている場合、JWT生成・検証が正常に動作する"""
        import importlib
        import app.domain.jwt as jwt_module
        
        # 元の環境変数を保存
        original_value = os.environ.get("JWT_SECRET_KEY")
        
        # 環境変数を設定
        test_secret = "test-secret-for-jwt-operations"
        os.environ["JWT_SECRET_KEY"] = test_secret
        
        # jwtモジュールを再インポートして環境変数を読み込ませる
        importlib.reload(jwt_module)
        
        # JWT生成・検証が正常に動作することを確認
        data = {"sub": "user@example.com"}
        token = jwt_module.create_access_token(data)
        
        # トークンが生成されることを確認
        assert isinstance(token, str)
        assert len(token) > 0
        
        # トークンを検証できることを確認
        payload = jwt_module.verify_token(token)
        assert payload["sub"] == "user@example.com"
        
        # クリーンアップ：元の値を復元
        if original_value is not None:
            os.environ["JWT_SECRET_KEY"] = original_value
        else:
            del os.environ["JWT_SECRET_KEY"]
        importlib.reload(jwt_module)
