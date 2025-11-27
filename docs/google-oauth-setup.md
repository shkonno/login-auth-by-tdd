# Google OAuth設定手順

このドキュメントでは、Google OAuth認証を設定する手順を説明します。

## 1. Google Cloud Consoleでの設定

### 1.1 プロジェクトの作成

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成（または既存のプロジェクトを選択）

### 1.2 OAuth同意画面の設定

1. 左メニューから「APIとサービス」→「OAuth同意画面」を選択
2. ユーザータイプを選択（外部ユーザーまたは内部ユーザー）
3. アプリ情報を入力：
   - アプリ名: TDD Training Auth
   - ユーザーサポートメール: あなたのメールアドレス
   - デベロッパーの連絡先情報: あなたのメールアドレス
4. スコープを追加：
   - `openid`
   - `https://www.googleapis.com/auth/userinfo.email`
   - `https://www.googleapis.com/auth/userinfo.profile`
5. テストユーザーを追加（外部ユーザーの場合、テスト中に使用するメールアドレス）

### 1.3 OAuth 2.0 クライアントIDの作成

1. 左メニューから「APIとサービス」→「認証情報」を選択
2. 「認証情報を作成」→「OAuth 2.0 クライアントID」を選択
3. アプリケーションの種類を選択：
   - **Webアプリケーション**を選択
4. 名前を入力（例: "TDD Training Web Client"）
5. 承認済みのリダイレクトURIを追加：
   - `http://localhost:3000/auth/google/callback`（開発環境）
   - 本番環境のURLも追加（例: `https://yourdomain.com/auth/google/callback`）
6. 「作成」をクリック
7. **クライアントID**と**クライアントシークレット**をコピーして保存

## 2. 環境変数の設定

### 2.1 .envファイルの作成

`backend/.env.example`をコピーして`backend/.env`を作成：

```bash
cp backend/.env.example backend/.env
```

### 2.2 環境変数の設定

`backend/.env`ファイルを編集して、取得したクライアントIDとシークレットを設定：

```env
GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback
```

## 3. 設定の確認

設定が正しく読み込まれているか確認するには、以下のコマンドを実行：

```python
from app.domain.oauth_config import is_google_oauth_configured

if is_google_oauth_configured():
    print("Google OAuth設定が完了しています")
else:
    print("Google OAuth設定が不完全です。.envファイルを確認してください")
```

## 4. 注意事項

- **クライアントシークレットは機密情報です**。Gitにコミットしないでください
- `.env`ファイルは`.gitignore`に含まれていることを確認してください
- 本番環境では、環境変数を直接設定するか、シークレット管理サービスを使用してください
- リダイレクトURIは、Google Cloud Consoleで設定したものと完全に一致する必要があります

## 5. トラブルシューティング

### リダイレクトURI不一致エラー

エラーメッセージ: `redirect_uri_mismatch`

**解決方法**: Google Cloud Consoleで設定したリダイレクトURIと、`.env`ファイルの`GOOGLE_REDIRECT_URI`が一致しているか確認してください。

### クライアントID/シークレットが見つからない

**解決方法**: 
1. Google Cloud Consoleで認証情報を確認
2. `.env`ファイルの環境変数名が正しいか確認（大文字小文字に注意）
3. アプリケーションを再起動して環境変数を読み込み直す

## 参考リンク

- [Google OAuth 2.0 ドキュメント](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)

