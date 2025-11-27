# TDDセッション記録: Issue #13, #14 LoginService実装と認証エラーハンドリング

**日時**: 2025-11-27T01:54:00Z  
**ブランチ**: `feature/issue-13-14-login-service`  
**PR**: #5

---

## セッション概要

Issue #13（LoginService実装）とIssue #14（認証エラーハンドリング）をTDDで実装し、プロパティベースドテストを追加しました。また、Gitのブランチ作成とプルリクエストの仕組みについても理解を深めました。

---

## 実施内容

### 1. Issue #13: LoginService実装

#### Red Phase（テスト作成）
- `backend/tests/domain/test_login.py`を作成
- 最初のテストケース: `test_login_with_valid_credentials`
- テスト実行 → `ModuleNotFoundError`（期待通り）

#### Green Phase（実装）
- `backend/app/domain/login_service.py`を作成
- `LoginService`クラスを実装
  - 依存性注入（repository, verifier, token_creator）
  - `login(email, password)`メソッド
  - ユーザー検索 → パスワード検証 → JWT生成の流れ
- テスト実行 → ✅ PASSED

#### 実装した機能
- メールアドレスとパスワードでログイン
- JWTトークンの生成と返却
- 依存性注入によるテスト容易性の確保

---

### 2. Issue #14: 認証エラーハンドリング

#### Red Phase（テスト作成）
1. **存在しないメールアドレスのテスト**
   - `test_login_with_nonexistent_email_raises_error`
   - ✅ PASSED（既存実装で対応済み）

2. **間違ったパスワードのテスト**
   - `test_login_with_wrong_password_raises_error`
   - ✅ PASSED（既存実装で対応済み）

3. **無効なユーザーのテスト**
   - `test_login_with_inactive_user_raises_error`
   - ❌ FAILED（`is_active`チェックが未実装）

#### Green Phase（実装）
- `LoginService.login()`に`is_active`チェックを追加
- テスト実行 → ✅ PASSED

#### 実装したエラーハンドリング
- 存在しないメールアドレス → `ValueError("Invalid email or password")`
- 間違ったパスワード → `ValueError("Invalid email or password")`
- 無効なユーザー（`is_active=False`） → `ValueError("Invalid email or password")`

---

### 3. プロパティベースドテスト追加

#### 追加したテストケース（5つ）

1. **`test_any_valid_login_succeeds`**
   - 有効なメールとパスワードなら常にログインできる
   - hypothesisでランダムなメール・パスワードを生成してテスト

2. **`test_nonexistent_email_always_raises_error`**
   - 存在しないメールアドレスなら常にエラーになる

3. **`test_wrong_password_always_raises_error`**
   - 間違ったパスワードなら常にエラーになる

4. **`test_inactive_user_always_raises_error`**
   - 無効なユーザーなら常にエラーになる

5. **`test_login_token_always_has_valid_format`**
   - ログイン成功時は常に有効な形式のJWTトークンが返される

#### 技術的な課題と解決

**メールアドレスの正規化問題**
- hypothesisが生成したメールアドレスが、Userエンティティに保存される際に正規化される
- 解決: 保存後に実際のメールアドレスを取得して使用

```python
saved_user = repository.find_by_email(user.email)
assert saved_user is not None
actual_email = saved_user.email
token = service.login(actual_email, password)
```

---

## テスト結果

```
tests/domain/test_login.py::test_login_with_valid_credentials PASSED
tests/domain/test_login.py::test_login_with_nonexistent_email_raises_error PASSED
tests/domain/test_login.py::test_login_with_wrong_password_raises_error PASSED
tests/domain/test_login.py::test_login_with_inactive_user_raises_error PASSED
tests/domain/test_login.py::test_any_valid_login_succeeds PASSED
tests/domain/test_login.py::test_nonexistent_email_always_raises_error PASSED
tests/domain/test_login.py::test_wrong_password_always_raises_error PASSED
tests/domain/test_login.py::test_inactive_user_always_raises_error PASSED
tests/domain/test_login.py::test_login_token_always_has_valid_format PASSED

9 passed, 1 warning
```

---

## Git操作とプルリクエスト

### ブランチ作成とコミット

```bash
# 新しいブランチを作成
git checkout -b feature/issue-13-14-login-service

# Issue 13のコミット
git commit -m "feat: Issue #13 LoginService実装"

# Issue 14のコミット
git commit -m "feat: Issue #14 認証エラーハンドリング + プロパティベースドテスト"

# ドキュメント更新
git commit -m "docs: Issue #13, #14 完了マーク"
```

### リモートへのプッシュ

```bash
git push -u origin feature/issue-13-14-login-service
```

### プルリクエスト作成

- **PR #5**: `feat: Issue #13, #14 LoginService実装と認証エラーハンドリング`
- **URL**: https://github.com/shkonno/tdd-training/pull/5
- **Base**: `main`
- **Head**: `feature/issue-13-14-login-service`
- **状態**: Open

---

## Gitのブランチ作成とプルリクエストの仕組み

### 重要な理解

1. **リモートブランチは直接作成できない**
   - 必ずローカルでブランチを作成してから`git push`する
   - `git push`でリモートブランチが作成される

2. **プルリクエストは自動で作成されない**
   - `git push`してもプルリクエストは作成されない
   - 手動で作成する必要がある（GitHub MCPまたはWeb UI）

3. **フォークの構造**
   ```
   オリジナルリポジトリ: o-shige/tdd-training
       ↓ フォーク
   自分のリポジトリ: shkonno/tdd-training ← これがorigin
   ```
   - 自分のリポジトリにプッシュしても、オリジナルリポジトリには影響しない

### ブランチ作成コマンドの違い

- **`git branch <name>`**: ブランチ作成のみ（切り替えはしない）
- **`git checkout -b <name>`**: ブランチ作成と切り替えを同時に（推奨）
- **`git switch -c <name>`**: `checkout -b`と同じ（Git 2.23+）

### ワークフローの注意点

- **`git checkout main`は不要な場合が多い**
  - 既に作業中のブランチがある場合は、そのブランチで作業を続ける
  - 新しいブランチが必要な場合のみ、mainに切り替える（その前に変更をコミットまたはstash）

---

## 作成・変更ファイル

### 新規作成
- `backend/app/domain/login_service.py` - LoginService実装
- `backend/tests/domain/test_login.py` - テストケース（9テストケース）

### 更新
- `issues.md` - Issue #13, #14を完了にマーク

---

## 学習ポイント

### TDDの実践
- Red → Green → Refactorサイクルを徹底
- テストが失敗することを確認してから実装
- プロパティベースドテストで品質を担保

### 依存性注入の活用
- `verifier`と`token_creator`を依存性注入することで、テストの高速化を実現
- bcryptは遅いため、テスト用の高速な関数を使用

### エラーハンドリング
- セキュリティ上の理由から、具体的なエラー内容を返さない
- 「Invalid email or password」という統一されたメッセージで返す

### Gitの理解
- ブランチ作成とプッシュの仕組み
- フォーク環境での作業フロー
- プルリクエストの作成方法

---

## 次のステップ

- Issue #15: Redisセッションストア
- Issue #16: ログインAPIエンドポイント
- Issue #17: ログインフォームUI
- Issue #18: 保護されたルート（/users/me）
- Issue #19: ダッシュボードUI

---

## コミット履歴

1. `feat: Issue #13 LoginService実装`
2. `feat: Issue #14 認証エラーハンドリング + プロパティベースドテスト`
3. `docs: Issue #13, #14 完了マーク`

---

## 参考

- t_wada式TDD: 「動作するきれいなコード」を目指す
- Kent Beck: テストファースト、小さなステップ
- Tidy First?: リファクタリングを先に行う判断


