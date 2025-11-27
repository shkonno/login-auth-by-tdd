"""SessionStoreのテスト"""

import pytest
import redis
from hypothesis import given, strategies as st
from typing import Optional
from app.domain.session_store import SessionStore
from app.infrastructure.session_store import RedisSessionStore


class InMemorySessionStore(SessionStore):
    """テスト用のインメモリSessionStore実装"""

    def __init__(self):
        self._sessions = {}

    def save(self, session_id: str, data: dict, ttl: Optional[int] = None) -> None:
        self._sessions[session_id] = data

    def get(self, session_id: str) -> Optional[dict]:
        return self._sessions.get(session_id)

    def delete(self, session_id: str) -> None:
        if session_id in self._sessions:
            del self._sessions[session_id]


def test_save_and_get_session():
    """セッションを保存して取得できる"""
    # Arrange
    store = InMemorySessionStore()
    session_id = "test-session-123"
    session_data = {"user_id": "user-456", "email": "test@example.com"}

    # Act
    store.save(session_id, session_data)
    retrieved_data = store.get(session_id)

    # Assert
    assert retrieved_data is not None
    assert retrieved_data == session_data
    assert retrieved_data["user_id"] == "user-456"
    assert retrieved_data["email"] == "test@example.com"


def test_delete_session():
    """セッションを削除できる"""
    # Arrange
    store = InMemorySessionStore()
    session_id = "test-session-123"
    session_data = {"user_id": "user-456"}

    # Act
    store.save(session_id, session_data)
    store.delete(session_id)
    retrieved_data = store.get(session_id)

    # Assert
    assert retrieved_data is None


def test_get_nonexistent_session_returns_none():
    """存在しないセッションIDで取得するとNoneが返る"""
    # Arrange
    store = InMemorySessionStore()

    # Act
    retrieved_data = store.get("nonexistent-session-id")

    # Assert
    assert retrieved_data is None


def test_update_session():
    """既存のセッションIDでデータを更新できる"""
    # Arrange
    store = InMemorySessionStore()
    session_id = "test-session-123"
    initial_data = {"user_id": "user-456", "email": "old@example.com"}
    updated_data = {"user_id": "user-456", "email": "new@example.com"}

    # Act
    store.save(session_id, initial_data)
    store.save(session_id, updated_data)
    retrieved_data = store.get(session_id)

    # Assert
    assert retrieved_data is not None
    assert retrieved_data == updated_data
    assert retrieved_data["email"] == "new@example.com"


# Redis実装のテスト
@pytest.fixture
def redis_client():
    """テスト用のRedisクライアント"""
    client = redis.from_url("redis://redis:6379", decode_responses=True)
    # テスト前にデータベースをクリア
    client.flushdb()
    yield client
    # テスト後にデータベースをクリア
    client.flushdb()


@pytest.fixture
def redis_session_store(redis_client):
    """RedisSessionStoreのインスタンス"""
    return RedisSessionStore(redis_client=redis_client)


def test_redis_save_and_get_session(redis_session_store):
    """Redisでセッションを保存して取得できる"""
    # Arrange
    session_id = "redis-session-123"
    session_data = {"user_id": "user-456", "email": "test@example.com"}

    # Act
    redis_session_store.save(session_id, session_data)
    retrieved_data = redis_session_store.get(session_id)

    # Assert
    assert retrieved_data is not None
    assert retrieved_data == session_data
    assert retrieved_data["user_id"] == "user-456"
    assert retrieved_data["email"] == "test@example.com"


def test_redis_delete_session(redis_session_store):
    """Redisでセッションを削除できる"""
    # Arrange
    session_id = "redis-session-123"
    session_data = {"user_id": "user-456"}

    # Act
    redis_session_store.save(session_id, session_data)
    redis_session_store.delete(session_id)
    retrieved_data = redis_session_store.get(session_id)

    # Assert
    assert retrieved_data is None


def test_redis_get_nonexistent_session_returns_none(redis_session_store):
    """Redisで存在しないセッションIDで取得するとNoneが返る"""
    # Act
    retrieved_data = redis_session_store.get("nonexistent-session-id")

    # Assert
    assert retrieved_data is None


def test_redis_session_with_ttl(redis_session_store, redis_client):
    """RedisでセッションにTTL（有効期限）を設定できる"""
    # Arrange
    session_id = "redis-session-ttl-123"
    session_data = {"user_id": "user-456"}
    ttl = 5  # 5秒

    # Act
    redis_session_store.save(session_id, session_data, ttl=ttl)
    
    # TTLが設定されていることを確認
    ttl_value = redis_client.ttl(session_id)
    assert ttl_value > 0
    assert ttl_value <= ttl
    
    # セッションが取得できることを確認
    retrieved_data = redis_session_store.get(session_id)
    assert retrieved_data is not None
    assert retrieved_data == session_data


@given(
    session_id=st.text(min_size=1, max_size=100),
    user_id=st.text(min_size=1, max_size=100),
    email=st.emails()
)
def test_save_and_get_session_with_various_data(session_id: str, user_id: str, email: str):
    """様々なセッションIDとデータでセッションを保存・取得できる（PBT）"""
    # Arrange
    store = InMemorySessionStore()
    session_data = {"user_id": user_id, "email": email}

    # Act
    store.save(session_id, session_data)
    retrieved_data = store.get(session_id)

    # Assert
    assert retrieved_data is not None
    assert retrieved_data == session_data
    assert retrieved_data["user_id"] == user_id
    assert retrieved_data["email"] == email


@given(
    session_id=st.text(min_size=1, max_size=100),
    ttl=st.integers(min_value=1, max_value=3600)
)
def test_session_ttl_with_various_values(session_id: str, ttl: int):
    """様々なTTL値でセッションを保存できる（PBT）"""
    # Arrange
    store = InMemorySessionStore()
    session_data = {"user_id": "user-123"}

    # Act
    store.save(session_id, session_data, ttl=ttl)
    retrieved_data = store.get(session_id)

    # Assert
    assert retrieved_data is not None
    assert retrieved_data == session_data

