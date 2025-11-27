"""Redis SessionStore実装

【このファイルの目的】
SessionStoreインターフェースをRedisで実装します。

【実装のポイント】
1. Redisへの接続管理
2. JSON形式でのデータ保存・取得
3. TTL（有効期限）の設定
4. エラーハンドリング
"""

import json
from typing import Optional, Dict, Any
import redis

from app.domain.session_store import SessionStore
from app.infrastructure.redis_client import get_redis_client


class RedisSessionStore(SessionStore):
    """Redisを使ったSessionStore実装

    【なぜRedisを使う？】
    - 高速な読み書き（メモリベース）
    - TTL（有効期限）の自動管理
    - スケーラブル（複数のサーバーで共有可能）

    【データ形式】
    RedisにはJSON文字列として保存します。
    例: {"user_id": "123", "email": "test@example.com"}
    """

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """SessionStoreを初期化

        Args:
            redis_client: Redisクライアント（テスト用に注入可能）
        """
        self._redis = redis_client or get_redis_client()

    def save(self, session_id: str, data: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """セッションをRedisに保存する

        Args:
            session_id: セッションID（Redisのキー）
            data: 保存するデータ（辞書形式）
            ttl: 有効期限（秒単位）。Noneの場合は無期限

        【処理の流れ】
        1. データをJSON文字列に変換
        2. Redisに保存
        3. TTLが指定されていれば設定
        """
        json_data = json.dumps(data)
        if ttl is not None:
            self._redis.setex(session_id, ttl, json_data)
        else:
            self._redis.set(session_id, json_data)

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """セッションをRedisから取得する

        Args:
            session_id: セッションID

        Returns:
            セッションデータ（辞書形式）。見つからない場合はNone

        【処理の流れ】
        1. Redisからデータを取得
        2. JSON文字列を辞書に変換
        3. 見つからなければNoneを返す
        """
        json_data = self._redis.get(session_id)
        if json_data is None:
            return None
        return json.loads(json_data)

    def delete(self, session_id: str) -> None:
        """セッションをRedisから削除する

        Args:
            session_id: セッションID
        """
        self._redis.delete(session_id)

