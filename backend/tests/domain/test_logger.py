"""ロガーのテスト"""

import logging

import pytest

from app.domain.logger import get_logger, configure_logging


class TestLoggerConfiguration:
    """ロガー設定のテスト"""

    def test_ロガーが設定されている(self):
        """ロガーが正しく初期化されている"""
        logger = get_logger(__name__)
        
        assert logger is not None
        assert isinstance(logger, logging.Logger)

    def test_ログレベルが設定されている(self):
        """ログレベルが適切に設定されている"""
        configure_logging()
        logger = get_logger(__name__)
        
        # ルートロガーのレベルが設定されていることを確認
        root_logger = logging.root
        assert root_logger.level >= logging.DEBUG
        assert root_logger.level <= logging.CRITICAL

    def test_ログ出力が動作する(self):
        """ログ出力が正常に動作する"""
        import io
        
        # ログ設定をリセット
        logging.root.handlers = []
        configure_logging()
        
        # ログ出力をキャプチャするためのストリームを作成
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        
        logger = get_logger(__name__)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # ログを出力
        logger.info("Test log message")
        
        # ログが出力されていることを確認
        log_output = log_capture.getvalue()
        assert "Test log message" in log_output


class TestLoggerSecurity:
    """ロガーのセキュリティ考慮事項のテスト"""

    def test_パスワードがログに出力されない(self):
        """パスワードがログに出力されないことを確認"""
        import io
        from app.domain.logger import sanitize_log_message
        
        # ログ設定をリセット
        logging.root.handlers = []
        configure_logging()
        
        # ログ出力をキャプチャ
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(message)s"))
        
        logger = get_logger(__name__)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # パスワードを含むメッセージをログ出力
        password = "secret_password_123"
        message = f"User login attempt with password: {password}"
        sanitized_message = sanitize_log_message(message)
        logger.info(sanitized_message)
        
        # ログにパスワードが含まれていないことを確認
        log_output = log_capture.getvalue()
        assert password not in log_output
        assert "***" in log_output or "[REDACTED]" in log_output

    def test_トークンがログに出力されない(self):
        """トークンがログに出力されないことを確認"""
        import io
        from app.domain.logger import sanitize_log_message
        
        # ログ設定をリセット
        logging.root.handlers = []
        configure_logging()
        
        # ログ出力をキャプチャ
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(message)s"))
        
        logger = get_logger(__name__)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # トークンを含むメッセージをログ出力
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0"
        message = f"Access token: {token}"
        sanitized_message = sanitize_log_message(message)
        logger.info(sanitized_message)
        
        # ログにトークンが含まれていないことを確認
        log_output = log_capture.getvalue()
        assert token not in log_output
        assert "***" in log_output or "[REDACTED]" in log_output

