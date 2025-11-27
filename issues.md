# TDD JWT認証プロジェクト - イシューリスト

## Week 1: 基盤構築 + 純粋関数のTDD

| # | イシュー | TDDテスト対象 | 優先度 | 状態 |
|---|----------|--------------|--------|------|
| 1 | Docker Compose環境セットアップ | - | High | [x] |
| 2 | FastAPIスケルトン作成 | - | High | [x] |
| 3 | Next.jsスケルトン作成 | - | High | [x] |
| 4 | pytest環境構築 | - | High | [x] |
| 5 | パスワードハッシュ化機能 | `test_password.py` | High | [x] |
| 6 | JWT生成・検証機能 | `test_jwt.py` | High | [x] |

---

## Week 2: ユーザー登録のTDD + UI

| # | イシュー | TDDテスト対象 | 優先度 | 状態 |
|---|----------|--------------|--------|------|
| 7 | Userドメインエンティティ | `test_user_registration.py` | High | [ｘ] |
| 8 | UserRepositoryインターフェース | `test_user_registration.py` | High | [x] |
| 9 | RegistrationService | `test_user_registration.py` | High | [x] |
| 10 | SQLAlchemy UserRepository実装 | `test_user_repository.py` | High | [ ] |
| 11 | 登録APIエンドポイント | `test_registration_endpoint.py` | High | [ ] |
| 12 | 登録フォームUI（Next.js） | E2Eテスト（任意） | Medium | [ ] |
| 12a | 品質保証観点でのテスト | 全テスト（任意） | Medium | [ ] |

---

## Week 3: ログイン + セッション管理の TDD

| #   | イシュー                      | TDD テスト対象            | 優先度 | 状態 |
| --- | ----------------------------- | ------------------------- | ------ | ---- |
| 13  | LoginService 実装             | `test_login.py`           | High   | [x]  |
| 14  | 認証エラーハンドリング        | `test_login.py`           | High   | [x]  |
| 15  | Redis セッションストア        | `test_session.py`         | High   | [x]  |
| 16  | ログイン API エンドポイント   | `test_login_endpoint.py`  | High   | [x]  |
| 17  | ログインフォーム UI           | E2E テスト（任意）        | Medium | [x]  |
| 18  | 保護されたルート（/users/me） | `test_protected_route.py` | High   | [x]  |
| 19  | ダッシュボード UI             | E2E テスト（任意）        | Medium | [x]  |

---

## Week 4: トークンリフレッシュ + OAuth

| #   | イシュー                  | TDD テスト対象             | 優先度 | 状態 |
| --- | ------------------------- | -------------------------- | ------ | ---- |
| 20  | リフレッシュトークン生成  | `test_refresh_token.py`    | High   | [x]  |
| 21  | アクセストークン更新 API  | `test_refresh_endpoint.py` | High   | [x]  |
| 22  | Google OAuth 設定         | -                          | Medium | [x]  |
| 23  | GoogleOAuthService        | `test_oauth.py`            | High   | [x]  |
| 24  | OAuth コールバック API    | `test_oauth_callback.py`   | High   | [x]  |
| 25  | Google ログインボタン追加 | E2E テスト（任意）         | Medium | [ ]  |

---

## 横断的イシュー

| #   | イシュー                     | 備考                        | 状態 |
| --- | ---------------------------- | --------------------------- | ---- |
| 26  | .gitignore 作成              | Python + Node.js 用         | [x]  |
| 27  | CI/CD 設定（GitHub Actions） | テスト自動実行              | [x]  |
| 28  | エラーハンドリング共通化     | カスタム例外クラス          | [ ]  |
| 29  | API 仕様書（OpenAPI）        | FastAPI 自動生成            | [ ]  |
| 30  | SECRET_KEY 等を環境変数化    | JWT 設定を.env から読み込み | [ ]  |
| 31  | Logger                      |影響大きい | [ ]  |

---

## TDDサイクルの進め方

各イシューは以下のサイクルで進める：

1. **Red**: 失敗するテストを書く（10分）
2. **Green**: 最小限の実装でテストを通す（20分）
3. **Refactor**: コードをきれいにする（10分）
4. **UI確認**: Docker起動してブラウザで動作確認（10分）
5. **Git commit**: 1サイクルごとにコミット（5分）

---

## 参考資料

- t_wada式TDD: 「動作するきれいなコード」を目指す
- Kent Beck: テストファースト、小さなステップ
- Tidy First?: リファクタリングを先に行う判断
