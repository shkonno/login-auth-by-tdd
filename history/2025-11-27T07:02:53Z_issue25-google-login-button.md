# Issue 25: Google ログインボタン追加

## セッション概要

- **日時**: 2025-11-27
- **イシュー**: #25 Google ログインボタン追加
- **状態**: 実装完了（Google OAuth設定は先送り）

## 実装内容

### 1. ログインページの作成

**ファイル**: `frontend/app/login/page.tsx`

- Next.js App Routerを使用したログインページ
- Google OAuth認証URLを生成する機能
- 環境変数から`NEXT_PUBLIC_GOOGLE_CLIENT_ID`を読み込み
- Google認証ページへのリダイレクト処理

**主な機能**:
- Google OAuth認証URLの生成
- リダイレクトURIの動的設定（`window.location.origin`を使用）
- エラーハンドリング（環境変数未設定時のアラート）

### 2. OAuthコールバックページの実装

**ファイル**: `frontend/app/auth/google/callback/page.tsx`

- Google認証後のコールバック処理
- バックエンドAPI（`/auth/google/callback`）を呼び出し
- JWTトークン（アクセストークン・リフレッシュトークン）の取得
- localStorageへのトークン保存
- エラーハンドリングとデバッグログの追加

**処理フロー**:
1. URLパラメータから認証コードを取得
2. バックエンドAPIに認証コードを送信
3. JWTトークンを取得してlocalStorageに保存
4. ホームページにリダイレクト

### 3. バックエンドCORS設定の追加

**ファイル**: `backend/main.py`

- FastAPIのCORSミドルウェアを追加
- フロントエンド（`http://localhost:3000`）からのリクエストを許可
- 認証情報（credentials）の送信を許可

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Docker Compose環境変数の設定

**ファイル**: `docker-compose.yml`

- バックエンドとフロントエンドの環境変数を設定
- `.env`ファイルから環境変数を読み込む設定
- フロントエンド用の`NEXT_PUBLIC_`プレフィックス付き環境変数

**設定項目**:
- `GOOGLE_CLIENT_ID`: Google OAuthクライアントID
- `GOOGLE_CLIENT_SECRET`: Google OAuthクライアントシークレット
- `GOOGLE_REDIRECT_URI`: OAuthリダイレクトURI
- `NEXT_PUBLIC_GOOGLE_CLIENT_ID`: フロントエンド用クライアントID
- `NEXT_PUBLIC_GOOGLE_REDIRECT_URI`: フロントエンド用リダイレクトURI
- `NEXT_PUBLIC_BACKEND_URL`: バックエンドAPIのURL

### 5. 環境変数ファイルのテンプレート作成

**ファイル**: `.env.example`

- 必要な環境変数のテンプレートを作成
- Google OAuth設定の説明を追加

## 発生した問題と解決

### 問題1: フロントエンドサーバーが起動していない

**症状**: `ERR_CONNECTION_REFUSED`エラーが発生

**原因**: Docker Composeでフロントエンドコンテナが起動していなかった

**解決**: `docker-compose up -d frontend`でフロントエンドコンテナを起動

### 問題2: 環境変数が設定されていない

**症状**: `NEXT_PUBLIC_GOOGLE_CLIENT_IDが設定されていません`というエラー

**原因**: `.env`ファイルが存在しない、またはプレースホルダーのまま

**解決策**:
1. `.env.example`ファイルを作成してテンプレートを提供
2. `docker-compose.yml`で環境変数の設定を追加
3. ユーザーが実際のGoogle Client IDを設定する必要があることを説明

**注意**: Google OAuth設定は先送りとし、実装自体は完了

## 実装ファイル一覧

### 新規作成ファイル

1. `frontend/app/login/page.tsx` - ログインページ
2. `frontend/app/auth/google/callback/page.tsx` - OAuthコールバックページ
3. `.env.example` - 環境変数テンプレート

### 変更ファイル

1. `backend/main.py` - CORS設定を追加
2. `docker-compose.yml` - 環境変数設定を追加
3. `issues.md` - issue25を完了としてマーク

## 次のステップ

### 未完了項目

1. **Google OAuth設定**: Google Cloud ConsoleでクライアントIDを取得して`.env`ファイルに設定
2. **動作確認**: Google OAuth設定後に実際の認証フローをテスト

### 次のイシュー

- **Issue 28**: エラーハンドリング共通化（カスタム例外クラスの作成）

## 技術的な学び

1. **Next.js App Router**: `'use client'`ディレクティブが必要（クライアントコンポーネント）
2. **環境変数**: Next.jsでは`NEXT_PUBLIC_`プレフィックスが必要（クライアント側で使用する場合）
3. **CORS設定**: フロントエンドとバックエンドが異なるポートで動作する場合、CORS設定が必須
4. **Docker Compose**: 環境変数は`.env`ファイルから自動的に読み込まれる

## 参考資料

- [Google OAuth設定手順](./docs/google-oauth-setup.md)
- [Next.js Environment Variables](https://nextjs.org/docs/app/building-your-application/configuring/environment-variables)
- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)

