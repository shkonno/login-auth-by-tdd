"""Userドメインエンティティのテスト"""

import pytest
from pydantic import ValidationError

from app.domain.user import User


def test_create_user_with_valid_attributes():
    """有効な属性でUserエンティティを作成できる"""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password_here"
    )

    assert user.email == "test@example.com"
    assert user.hashed_password == "hashed_password_here"
    assert user.id is not None  # UUIDが自動生成される
    assert user.is_active is True  # デフォルト値
    assert user.created_at is not None  # 自動設定される


def test_create_user_with_invalid_email_raises_error():
    """無効なメールアドレスでUserを作成するとエラーになる"""
    with pytest.raises(ValidationError):
        User(
            email="invalid-email",
            hashed_password="hashed_password_here"
        )


def test_create_user_with_empty_password_raises_error():
    """空のパスワードでUserを作成するとエラーになる"""
    with pytest.raises(ValidationError):
        User(
            email="test@example.com",
            hashed_password=""
        )


def test_create_user_with_empty_email_raises_error():
    """空のメールアドレスでUserを作成するとエラーになる"""
    with pytest.raises(ValidationError):
        User(
            email="",
            hashed_password="hashed_password_here"
        )


def test_user_repository_interface_has_save_method():
    """UserRepositoryインターフェースにsaveメソッドが定義されている"""
    from app.domain.user_repository import UserRepository

    assert hasattr(UserRepository, 'save')
