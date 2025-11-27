"""ロガー設定

【なぜこのファイルが必要？】
ログ出力を一元管理するため。
ログレベル、フォーマット、セキュリティ考慮事項を統一する。

【ログレベルの標準】
- DEBUG: 詳細なデバッグ情報
- INFO: 通常動作の情報
- WARNING: 警告・潜在的問題
- ERROR: エラー・機能停止
- CRITICAL: 重大なエラー・システム停止

【セキュリティ考慮事項】
ログに出力しないもの：
- passwords（パスワード）
- tokens（トークン）
- secrets（シークレット）
- full PII（完全な個人情報）
- full bodies with sensitive data（機密データを含む完全なボディ）
"""

import logging
import os
import re
from typing import Optional


def configure_logging(level: Optional[str] = None) -> None:
    """ログ設定を初期化する
    
    Args:
        level: ログレベル（環境変数LOG_LEVELから読み込む、デフォルトはINFO）
    """
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO")
    
    # ログレベルを文字列から数値に変換
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # ログフォーマットを設定
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # ルートロガーの設定
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        datefmt=date_format
    )


def sanitize_log_message(message: str) -> str:
    """ログメッセージから機密情報をマスキングする
    
    【マスキング対象】
    - password: パスワード関連の文字列
    - token: JWTトークンやアクセストークン
    - secret: シークレットキー
    
    Args:
        message: 元のログメッセージ
        
    Returns:
        機密情報がマスキングされたログメッセージ
    """
    # パスワード関連のパターン（password, pwd, passwdなど）
    password_patterns = [
        r'password["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        r'pwd["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        r'passwd["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
    ]
    
    # トークン関連のパターン（token, access_token, refresh_tokenなど）
    token_patterns = [
        r'token["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        r'access_token["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        r'refresh_token["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        r'bearer\s+([A-Za-z0-9\-_\.]+)',  # Bearerトークン
    ]
    
    # シークレット関連のパターン（secret, api_key, api_secretなど）
    secret_patterns = [
        r'secret["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        r'api_key["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        r'api_secret["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
    ]
    
    sanitized = message
    
    # パスワードをマスキング
    for pattern in password_patterns:
        sanitized = re.sub(pattern, lambda m: m.group(0).replace(m.group(1), "[REDACTED]"), sanitized, flags=re.IGNORECASE)
    
    # トークンをマスキング
    for pattern in token_patterns:
        sanitized = re.sub(pattern, lambda m: m.group(0).replace(m.group(1), "[REDACTED]"), sanitized, flags=re.IGNORECASE)
    
    # シークレットをマスキング
    for pattern in secret_patterns:
        sanitized = re.sub(pattern, lambda m: m.group(0).replace(m.group(1), "[REDACTED]"), sanitized, flags=re.IGNORECASE)
    
    return sanitized


def get_logger(name: str) -> logging.Logger:
    """ロガーを取得する
    
    Args:
        name: ロガー名（通常は__name__を使用）
        
    Returns:
        設定済みのロガーインスタンス
    """
    # ログ設定がまだ行われていない場合は初期化
    if not logging.root.handlers:
        configure_logging()
    
    return logging.getLogger(name)

