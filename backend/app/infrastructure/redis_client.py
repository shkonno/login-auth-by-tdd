"""Redisクライアント設定

【なぜこのファイルが必要？】
Redis接続を管理するための設定ファイルです。

【なぜ環境変数から読み込む？】
- 本番環境: 本番用のRedisサーバー
- テスト環境: テスト用のRedisサーバー
- 開発環境: docker-composeのRedis

環境変数で切り替えることで、同じコードで異なる環境に対応できます。
"""

import os
import redis

# Redis接続URL（環境変数から読み込み）
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")


def get_redis_client() -> redis.Redis:
    """Redisクライアントを取得する

    Returns:
        Redisクライアントインスタンス

    【なぜ関数で返す？】
    テスト時にモックや別のRedisインスタンスを返せるようにするため。
    依存性注入のパターンです。
    """
    return redis.from_url(REDIS_URL, decode_responses=True)

