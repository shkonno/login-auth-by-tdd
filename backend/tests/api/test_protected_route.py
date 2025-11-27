"""保護されたルート（/users/me）のテスト"""

import pytest
from hypothesis import given, strategies as st, settings
from fastapi.testclient import TestClient
from main import app
from app.domain.jwt import create_access_token
from datetime import timedelta
import uuid

client = TestClient(app)


def test_get_current_user_with_valid_token():
    """有効なトークンでアクセスするとユーザー情報が返される"""
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
    user_id = register_response.json()["id"]
    
    # ログインしてトークンを取得
    login_response = client.post(
        "/api/login",
        json={
            "email": unique_email,
            "password": password
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # 保護されたルートにアクセス
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert data["id"] == user_id
    assert data["email"] == unique_email


def test_get_current_user_without_token():
    """トークンなしでアクセスすると401 Unauthorizedが返される"""
    response = client.get("/api/users/me")
    
    assert response.status_code == 401
    assert "detail" in response.json()


def test_get_current_user_with_invalid_token():
    """無効なトークンでアクセスすると401 Unauthorizedが返される"""
    response = client.get(
        "/api/users/me",
        headers={"Authorization": "Bearer invalid-token-123"}
    )
    
    assert response.status_code == 401
    assert "detail" in response.json()


def test_get_current_user_with_expired_token():
    """期限切れトークンでアクセスすると401 Unauthorizedが返される"""
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
    user_id = register_response.json()["id"]
    
    # 期限切れのトークンを生成（過去の時刻に設定）
    expired_token = create_access_token(
        {"sub": user_id},
        expires_delta=timedelta(seconds=-1)  # 1秒前に期限切れ
    )
    
    # 保護されたルートにアクセス
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    
    assert response.status_code == 401
    assert "detail" in response.json()


@settings(deadline=2000, max_examples=10, suppress_health_check=[])  # 2秒のデッドライン、例数を制限
@given(
    password=st.text(min_size=8, max_size=20, alphabet=st.characters(min_codepoint=32, max_codepoint=126))
)
def test_get_current_user_with_various_valid_tokens(password: str):
    """様々な有効なトークンでユーザー情報を取得できる（PBT）"""
    # まずユーザーを登録（メールアドレスは常にユニークにする）
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    
    # ユーザー登録
    register_response = client.post(
        "/api/register",
        json={
            "email": unique_email,
            "password": password
        }
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]
    
    # ログインしてトークンを取得
    login_response = client.post(
        "/api/login",
        json={
            "email": unique_email,
            "password": password
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # 保護されたルートにアクセス
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert data["id"] == user_id
    assert data["email"] == unique_email


@given(
    invalid_token=st.text(min_size=1, max_size=200, alphabet=st.characters(min_codepoint=32, max_codepoint=126))
)
def test_get_current_user_with_various_invalid_tokens(invalid_token: str):
    """様々な無効なトークンでアクセスすると401エラーが返される（PBT）"""
    # 無効なトークンでアクセス
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )
    
    assert response.status_code == 401
    assert "detail" in response.json()

