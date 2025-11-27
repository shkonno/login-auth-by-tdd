"""LoginServiceのテスト"""

import pytest
from hypothesis import given, strategies as st
from app.domain.user import User
from app.domain.user_repository import UserRepository
from app.domain.login_service import LoginService


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


def test_login_with_valid_credentials():
    """有効なメールアドレスとパスワードでログインできる"""
    # Arrange
    repository = InMemoryUserRepository()
    # テスト用のユーザーを事前に登録（パスワードはハッシュ化済み）
    user = User(
        email="test@example.com",
        hashed_password="hashed_password123"
    )
    repository.save(user)
    
    # テスト用の高速パスワード検証関数
    def fast_verify(password: str, hashed: str) -> bool:
        return hashed == f"hashed_{password}"
    
    service = LoginService(repository, verifier=fast_verify)
    
    # Act
    token = service.login("test@example.com", "password123")
    
    # Assert
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_login_with_nonexistent_email_raises_error():
    """存在しないメールアドレスでログインするとエラーになる"""
    # Arrange
    repository = InMemoryUserRepository()
    # ユーザーは登録されていない
    
    # テスト用の高速パスワード検証関数
    def fast_verify(password: str, hashed: str) -> bool:
        return hashed == f"hashed_{password}"
    
    service = LoginService(repository, verifier=fast_verify)
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        service.login("nonexistent@example.com", "password123")
    
    # エラーメッセージを確認
    assert "Invalid email or password" in str(exc_info.value)


def test_login_with_wrong_password_raises_error():
    """間違ったパスワードでログインするとエラーになる"""
    # Arrange
    repository = InMemoryUserRepository()
    # テスト用のユーザーを事前に登録（正しいパスワードは"password123"）
    user = User(
        email="test@example.com",
        hashed_password="hashed_password123"
    )
    repository.save(user)
    
    # テスト用の高速パスワード検証関数
    def fast_verify(password: str, hashed: str) -> bool:
        return hashed == f"hashed_{password}"
    
    service = LoginService(repository, verifier=fast_verify)
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        service.login("test@example.com", "wrongpassword")
    
    # エラーメッセージを確認
    assert "Invalid email or password" in str(exc_info.value)


def test_login_with_inactive_user_raises_error():
    """無効なユーザー（is_active=False）でログインするとエラーになる"""
    # Arrange
    repository = InMemoryUserRepository()
    # 無効なユーザーを事前に登録
    user = User(
        email="inactive@example.com",
        hashed_password="hashed_password123",
        is_active=False
    )
    repository.save(user)
    
    # テスト用の高速パスワード検証関数
    def fast_verify(password: str, hashed: str) -> bool:
        return hashed == f"hashed_{password}"
    
    service = LoginService(repository, verifier=fast_verify)
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        service.login("inactive@example.com", "password123")
    
    # エラーメッセージを確認
    assert "Invalid email or password" in str(exc_info.value)


# LoginService プロパティベースドテスト

# テスト用の高速パスワード検証関数（bcryptは遅いのでテストでは使わない）
def fast_verify(password: str, hashed: str) -> bool:
    """テスト用の高速パスワード検証関数"""
    return hashed == f"hashed_{password}"


@given(st.emails(), st.text(min_size=1, max_size=100))
def test_any_valid_login_succeeds(email, password):
    """有効なメールとパスワードなら常にログインできる（プロパティベースド）"""
    repository = InMemoryUserRepository()
    # テスト用のユーザーを事前に登録
    user = User(
        email=email,
        hashed_password=f"hashed_{password}"
    )
    repository.save(user)
    
    # メールアドレスが正規化される可能性があるため、保存後のメールアドレスを使用
    saved_user = repository.find_by_email(user.email)
    assert saved_user is not None
    actual_email = saved_user.email
    
    service = LoginService(repository, verifier=fast_verify)
    
    token = service.login(actual_email, password)
    
    # ログイン成功時は常にJWTトークンが返される
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


@given(st.emails(), st.text(min_size=1, max_size=100))
def test_nonexistent_email_always_raises_error(email, password):
    """存在しないメールアドレスなら常にエラーになる（プロパティベースド）"""
    repository = InMemoryUserRepository()
    # ユーザーは登録されていない
    
    service = LoginService(repository, verifier=fast_verify)
    
    with pytest.raises(ValueError) as exc_info:
        service.login(email, password)
    
    assert "Invalid email or password" in str(exc_info.value)


@given(st.emails(), st.text(min_size=1, max_size=100), st.text(min_size=1, max_size=100))
def test_wrong_password_always_raises_error(email, correct_password, wrong_password):
    """間違ったパスワードなら常にエラーになる（プロパティベースド）"""
    # 正しいパスワードと間違ったパスワードが異なる場合のみテスト
    if correct_password == wrong_password:
        return
    
    repository = InMemoryUserRepository()
    # テスト用のユーザーを事前に登録（正しいパスワードで）
    user = User(
        email=email,
        hashed_password=f"hashed_{correct_password}"
    )
    repository.save(user)
    
    service = LoginService(repository, verifier=fast_verify)
    
    with pytest.raises(ValueError) as exc_info:
        service.login(email, wrong_password)
    
    assert "Invalid email or password" in str(exc_info.value)


@given(st.emails(), st.text(min_size=1, max_size=100))
def test_inactive_user_always_raises_error(email, password):
    """無効なユーザーなら常にエラーになる（プロパティベースド）"""
    repository = InMemoryUserRepository()
    # 無効なユーザーを事前に登録
    user = User(
        email=email,
        hashed_password=f"hashed_{password}",
        is_active=False
    )
    repository.save(user)
    
    service = LoginService(repository, verifier=fast_verify)
    
    with pytest.raises(ValueError) as exc_info:
        service.login(email, password)
    
    assert "Invalid email or password" in str(exc_info.value)


@given(st.emails(), st.text(min_size=1, max_size=100))
def test_login_token_always_has_valid_format(email, password):
    """ログイン成功時は常に有効な形式のJWTトークンが返される（プロパティベースド）"""
    repository = InMemoryUserRepository()
    # テスト用のユーザーを事前に登録
    user = User(
        email=email,
        hashed_password=f"hashed_{password}"
    )
    repository.save(user)
    
    # メールアドレスが正規化される可能性があるため、保存後のメールアドレスを使用
    saved_user = repository.find_by_email(user.email)
    assert saved_user is not None
    actual_email = saved_user.email
    
    service = LoginService(repository, verifier=fast_verify)
    
    token = service.login(actual_email, password)
    
    # JWTトークンは常に文字列で、長さがある
    assert isinstance(token, str)
    assert len(token) > 0
    # JWTトークンは通常、3つの部分（header.payload.signature）に分かれる
    # 最低限、ドットが含まれていることを確認
    assert "." in token

