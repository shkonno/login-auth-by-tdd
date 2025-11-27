"""ログインAPIエンドポイントのテスト"""

import pytest
from fastapi.testclient import TestClient
from main import app
import uuid

client = TestClient(app)


def test_login_with_valid_credentials():
    """有効なメールアドレスとパスワードでログインすると200 OKとトークンが返される"""
    # まずユーザーを登録
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    
    # ユーザー登録
    register_response = client.post(
        "/api/register",
        json={
            "email": unique_email,
            "password": password
        }
    )
    assert register_response.status_code == 201
    
    # ログイン
    response = client.post(
        "/api/login",
        json={
            "email": unique_email,
            "password": password
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


def test_login_with_invalid_email():
    """存在しないメールアドレスでログインすると401 Unauthorizedが返される"""
    response = client.post(
        "/api/login",
        json={
            "email": "nonexistent@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 401
    assert "detail" in response.json()


def test_login_with_wrong_password():
    """間違ったパスワードでログインすると401 Unauthorizedが返される"""
    # まずユーザーを登録
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    
    # ユーザー登録
    register_response = client.post(
        "/api/register",
        json={
            "email": unique_email,
            "password": password
        }
    )
    assert register_response.status_code == 201
    
    # 間違ったパスワードでログイン
    response = client.post(
        "/api/login",
        json={
            "email": unique_email,
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "detail" in response.json()


def test_login_with_invalid_json():
    """不正なJSONだと422 Unprocessable Entityが返される"""
    response = client.post(
        "/api/login",
        content="invalid json",
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 422


def test_login_with_missing_fields():
    """必須フィールドが不足していると422 Unprocessable Entityが返される"""
    response = client.post(
        "/api/login",
        json={
            "email": "test@example.com"
            # passwordが不足
        }
    )
    
    assert response.status_code == 422
    assert "detail" in response.json()

