"""GoogleOAuthServiceのテスト"""

import pytest
from unittest.mock import Mock

from app.domain.user import User
from app.domain.user_repository import UserRepository
from app.domain.oauth_service import GoogleOAuthService


class InMemoryUserRepository(UserRepository):
    """テスト用のインメモリUserRepository実装"""

    def __init__(self):
        self._users = {}

    def save(self, user: User) -> User:
        self._users[user.email] = user
        return user

    def find_by_email(self, email: str):
        return self._users.get(email)

    def find_by_id(self, user_id):
        for user in self._users.values():
            if user.id == user_id:
                return user
        return None


def test_Googleユーザー情報でユーザーを作成できる():
    """Googleから取得したユーザー情報でユーザーを作成できる"""
    # Arrange
    repository = InMemoryUserRepository()
    service = GoogleOAuthService(repository)
    google_user_info = {
        "email": "test@gmail.com",
        "name": "Test User",
        "sub": "google-user-id-123"
    }
    
    # Act
    user = service.authenticate(google_user_info)
    
    # Assert
    assert user is not None
    assert user.email == "test@gmail.com"
    # OAuth認証で作成されたユーザーはリポジトリに保存される
    saved_user = repository.find_by_email("test@gmail.com")
    assert saved_user is not None
    assert saved_user.email == "test@gmail.com"


def test_既存ユーザーの場合に既存ユーザーを返す():
    """同じメールアドレスのユーザーが既に存在する場合、既存ユーザーを返す"""
    # Arrange
    repository = InMemoryUserRepository()
    # 既存ユーザーを作成
    existing_user = User(
        email="existing@gmail.com",
        hashed_password="hashed_password"
    )
    repository.save(existing_user)
    
    service = GoogleOAuthService(repository)
    google_user_info = {
        "email": "existing@gmail.com",
        "name": "Updated Name",
        "sub": "google-user-id-456"
    }
    
    # Act
    user = service.authenticate(google_user_info)
    
    # Assert
    assert user is not None
    assert user.email == "existing@gmail.com"
    assert user.id == existing_user.id  # 同じユーザーID


def test_Googleユーザー情報にemailが欠けている場合にエラーが発生する():
    """Googleユーザー情報にemailが含まれていない場合、エラーが発生する"""
    # Arrange
    repository = InMemoryUserRepository()
    service = GoogleOAuthService(repository)
    google_user_info = {
        "name": "Test User",
        "sub": "google-user-id-123"
        # emailが欠けている
    }
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        service.authenticate(google_user_info)
    
    assert "email" in str(exc_info.value).lower()


def test_リポジトリに保存されたユーザーが返される():
    """authenticateメソッドはリポジトリに保存されたユーザーを返す"""
    # Arrange
    repository = InMemoryUserRepository()
    service = GoogleOAuthService(repository)
    google_user_info = {
        "email": "newuser@gmail.com",
        "name": "New User",
        "sub": "google-user-id-789"
    }
    
    # Act
    user = service.authenticate(google_user_info)
    
    # Assert
    assert user is not None
    # リポジトリから取得したユーザーと同じIDを持つ
    saved_user = repository.find_by_email("newuser@gmail.com")
    assert saved_user is not None
    assert user.id == saved_user.id


def test_Googleユーザー情報が空の場合にエラーが発生する():
    """Googleユーザー情報が空の場合、エラーが発生する"""
    # Arrange
    repository = InMemoryUserRepository()
    service = GoogleOAuthService(repository)
    google_user_info = {}
    
    # Act & Assert
    with pytest.raises(ValueError):
        service.authenticate(google_user_info)

