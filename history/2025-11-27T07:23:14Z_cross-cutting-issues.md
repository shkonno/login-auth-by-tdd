# TDD セッション記録 - 2025/11/27 07:23

## セッション概要

横断的イシュー（Issue #30, #28, #29, #31）をTDDで実装

---

## 実施内容

### Issue #30: SECRET_KEY等を環境変数化

#### 目的
JWT設定を環境変数から読み込むように変更し、セキュリティを向上させる

#### TDDサイクル

**Red Phase: テストケース作成**
- テストケース1: 環境変数からSECRET_KEYを読み込む
- テストケース2: 環境変数が設定されていない場合デフォルト値が使用される
- テストケース3: 環境変数設定時に既存のJWT機能が正常に動作する

**Green Phase: 実装**
- `backend/app/domain/jwt.py`: `os.getenv("JWT_SECRET_KEY", "your-secret-key-here")`で環境変数から読み込むように変更
- `docker-compose.yml`: `JWT_SECRET_KEY`環境変数を追加

**テスト結果**
- 全てのテストが通過（8個のJWTテスト、60個の全テスト）

#### 作成・変更ファイル
- `backend/app/domain/jwt.py` - 環境変数からSECRET_KEYを読み込むように変更
- `backend/tests/domain/test_jwt.py` - 環境変数読み込みのテストケース3つを追加
- `docker-compose.yml` - JWT_SECRET_KEY環境変数を追加

---

### Issue #28: エラーハンドリング共通化

#### 目的
エラー発生時の対応の切り分けと、それらを管理する箇所の一元化

#### TDDサイクル

**Red Phase: テストケース作成**
- テストケース1: カスタム例外クラスの基本構造（BusinessError, ValidationError, AuthenticationError, NotFoundError）
- テストケース2: 例外からHTTPステータスコードへの変換
- テストケース3: エラーレスポンス形式の統一

**Green Phase: 実装**
- `backend/app/domain/exceptions.py` - カスタム例外クラスと変換関数を実装
- `backend/app/domain/registration_service.py` - `ValueError`を`BusinessError`に置き換え
- `backend/app/domain/oauth_service.py` - `ValueError`を`ValidationError`に置き換え
- `backend/tests/domain/test_user_registration.py` - テストを`BusinessError`に更新
- `backend/tests/domain/test_oauth.py` - テストを`ValidationError`に更新

**テスト結果**
- 全てのテストが通過（14個の例外テスト、60個の全テスト）

#### 作成・変更ファイル
- `backend/app/domain/exceptions.py` - カスタム例外クラスと変換関数を新規作成
- `backend/app/domain/registration_service.py` - BusinessErrorに変更
- `backend/app/domain/oauth_service.py` - ValidationErrorに変更
- `backend/tests/domain/test_exceptions.py` - 例外クラスのテストを新規作成
- `backend/tests/domain/test_user_registration.py` - テストを更新
- `backend/tests/domain/test_oauth.py` - テストを更新

#### 実装した例外クラス
- `BusinessError` (400): ビジネスルール違反
- `ValidationError` (400): バリデーションエラー
- `AuthenticationError` (401): 認証エラー
- `NotFoundError` (404): リソース未検出

#### 実装した関数
- `convert_exception_to_http_status()`: 例外をHTTPステータスコードに変換
- `format_error_response()`: 例外を統一されたエラーレスポンス形式に変換

---

### Issue #29: API仕様書（OpenAPI）

#### 目的
FastAPIの自動生成機能を確認し、OpenAPI仕様書が正しく生成されていることを検証

#### TDDサイクル

**Red Phase: テストケース作成**
- テストケース1: OpenAPI仕様が生成されている
- テストケース2: エンドポイントのドキュメントが適切に記述されている
- テストケース3: レスポンスモデルが定義されている

**Green Phase: 確認**
- FastAPIは自動的にOpenAPI仕様を生成するため、追加実装は不要
- `/docs` (Swagger UI), `/redoc` (ReDoc), `/openapi.json` (OpenAPI JSON)が利用可能

**テスト結果**
- 全てのテストが通過（3個のOpenAPIテスト）

#### 作成ファイル
- `backend/tests/api/test_openapi.py` - OpenAPI仕様書のテストを新規作成

#### 確認したエンドポイント
- `http://localhost:8000/docs` - Swagger UI
- `http://localhost:8000/redoc` - ReDoc
- `http://localhost:8000/openapi.json` - OpenAPI JSON

---

### Issue #31: Logger

#### 目的
ログ出力を一元管理し、ログレベルとセキュリティ考慮事項を統一する

#### 業界標準確認
- **ログレベル**: Python標準（DEBUG, INFO, WARNING, ERROR, CRITICAL）に準拠 ✅
- **セキュリティ考慮事項**: OWASP標準に準拠 ✅
  - ログに出力しないもの: passwords, tokens, secrets, full PII, full bodies with sensitive data

#### TDDサイクル

**Red Phase: テストケース作成**
- テストケース1: ロガーが設定されている
- テストケース2: ログレベルが設定されている
- テストケース3: ログ出力が動作する
- テストケース4: パスワードがログに出力されない（セキュリティ）
- テストケース5: トークンがログに出力されない（セキュリティ）

**Green Phase: 実装**
- `backend/app/domain/logger.py` - ロガー設定機能とセキュリティ機能を実装

**テスト結果**
- 全てのテストが通過（5個のロガーテスト、68個の全テスト）

#### 作成ファイル
- `backend/app/domain/logger.py` - ロガー設定機能を新規作成
- `backend/tests/domain/test_logger.py` - ロガーのテストを新規作成

#### 実装した関数
- `configure_logging()`: ログ設定を初期化（環境変数`LOG_LEVEL`から読み込み、デフォルトはINFO）
- `get_logger()`: ロガーを取得
- `sanitize_log_message()`: ログメッセージから機密情報（パスワード、トークン、シークレット）をマスキング

#### ログレベル設定
- 環境変数`LOG_LEVEL`から読み込み（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- デフォルトはINFO

#### セキュリティ機能
- パスワード関連のパターンをマスキング（password, pwd, passwd）
- トークン関連のパターンをマスキング（token, access_token, refresh_token, bearer）
- シークレット関連のパターンをマスキング（secret, api_key, api_secret）
- マスキング結果: `[REDACTED]`

---

## TDDサイクルの流れ

各イシューは以下のサイクルで進めました：

1. **Red**: 失敗するテストを書く
2. **Green**: 最小限の実装でテストを通す
3. **Refactor**: コードをきれいにする
4. **テスト確認**: 既存のテストが壊れていないか確認

---

## テスト結果サマリー

- **Issue #30**: 8個のJWTテスト、60個の全テストが通過
- **Issue #28**: 14個の例外テスト、60個の全テストが通過
- **Issue #29**: 3個のOpenAPIテストが通過
- **Issue #31**: 5個のロガーテスト、68個の全テストが通過

**最終的なテスト数**: 68個のテストが全て通過 ✅

---

## 完了したイシュー

- ✅ Issue #30: SECRET_KEY等を環境変数化
- ✅ Issue #28: エラーハンドリング共通化
- ✅ Issue #29: API仕様書（OpenAPI）
- ✅ Issue #31: Logger

**全ての横断的イシューが完了しました**

---

## 参考資料

- t_wada式TDD: 「動作するきれいなコード」を目指す
- Kent Beck: テストファースト、小さなステップ
- RFC 5424: Syslog Severity Levels
- OWASP: Logging Security Best Practices

