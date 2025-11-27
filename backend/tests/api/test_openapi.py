"""OpenAPI仕様書のテスト"""

import json

import pytest
from fastapi.testclient import TestClient

from main import app


class TestOpenAPISpec:
    """OpenAPI仕様書のテスト"""

    def test_OpenAPI仕様が生成されている(self):
        """OpenAPI仕様が生成されていることを確認"""
        client = TestClient(app)
        
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        # JSONとしてパースできることを確認
        spec = response.json()
        assert isinstance(spec, dict)
        
        # OpenAPI仕様の必須フィールドを確認
        assert "openapi" in spec
        assert "info" in spec
        assert "paths" in spec
        
        # アプリケーション情報を確認
        assert spec["info"]["title"] == "Auth TDD Learning"
        assert spec["info"]["version"] == "0.1.0"

    def test_エンドポイントのドキュメントが適切に記述されている(self):
        """エンドポイントにsummaryやdescriptionが設定されていることを確認"""
        client = TestClient(app)
        
        response = client.get("/openapi.json")
        spec = response.json()
        
        # 主要なエンドポイントを確認
        paths = spec["paths"]
        
        # /auth/refreshエンドポイントのドキュメントを確認
        if "/auth/refresh" in paths:
            post_method = paths["/auth/refresh"].get("post", {})
            assert "summary" in post_method or "description" in post_method
        
        # /auth/google/callbackエンドポイントのドキュメントを確認
        if "/auth/google/callback" in paths:
            get_method = paths["/auth/google/callback"].get("get", {})
            assert "summary" in get_method or "description" in get_method

    def test_レスポンスモデルが定義されている(self):
        """エンドポイントのレスポンススキーマが定義されていることを確認"""
        client = TestClient(app)
        
        response = client.get("/openapi.json")
        spec = response.json()
        
        paths = spec["paths"]
        
        # /auth/refreshエンドポイントのレスポンスを確認
        if "/auth/refresh" in paths:
            post_method = paths["/auth/refresh"].get("post", {})
            responses = post_method.get("responses", {})
            # 200レスポンスが定義されていることを確認
            assert "200" in responses

