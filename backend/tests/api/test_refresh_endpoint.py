"""アクセストークン更新APIエンドポイントのテスト"""

from datetime import timedelta

import jwt
import pytest
from fastapi.testclient import TestClient

from app.domain.jwt import create_refresh_token, create_access_token, SECRET_KEY, ALGORITHM


def test_有効なリフレッシュトークンでアクセストークンを更新できる(app):
    """有効なリフレッシュトークンで新しいアクセストークンを取得できる"""
    # Arrange
    client = TestClient(app)
    user_id = "user-123"
    refresh_token = create_refresh_token({"sub": user_id})
    
    # Act
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


def test_期限切れリフレッシュトークンでエラーが返る(app):
    """期限切れのリフレッシュトークンで401エラーが返る"""
    # Arrange
    client = TestClient(app)
    user_id = "user-123"
    # 1秒前に期限切れのトークンを作成
    expired_token = create_refresh_token(
        {"sub": user_id},
        expires_delta=timedelta(seconds=-1)
    )
    
    # Act
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": expired_token}
    )
    
    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_無効なリフレッシュトークンでエラーが返る(app):
    """無効なトークンで401エラーが返る"""
    # Arrange
    client = TestClient(app)
    invalid_token = "invalid.token.here"
    
    # Act
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": invalid_token}
    )
    
    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_アクセストークンで更新しようとするとエラーが返る(app):
    """アクセストークン（type: refreshがない）で更新しようとすると401エラーが返る"""
    # Arrange
    client = TestClient(app)
    user_id = "user-123"
    access_token = create_access_token({"sub": user_id})
    
    # Act
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": access_token}
    )
    
    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_新しいアクセストークンに正しいユーザーIDが含まれる(app):
    """リフレッシュトークンのsubが新しいアクセストークンに含まれる"""
    # Arrange
    client = TestClient(app)
    user_id = "user-123"
    refresh_token = create_refresh_token({"sub": user_id})
    
    # Act
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    access_token = data["access_token"]
    
    # アクセストークンをデコードして検証
    payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == user_id
    assert "exp" in payload  # 有効期限が含まれる

