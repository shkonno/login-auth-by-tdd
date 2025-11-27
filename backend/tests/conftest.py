"""pytest設定とフィクスチャ"""

import pytest
from fastapi import FastAPI

from main import app as main_app


@pytest.fixture
def app():
    """FastAPIアプリケーションインスタンスを返す"""
    return main_app

