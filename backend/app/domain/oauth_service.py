"""Google OAuth認証サービス

【なぜこのファイルが必要？】
Google OAuth認証のビジネスロジックを担当します。

【処理の流れ】
1. Googleから取得したユーザー情報を受け取る
2. メールアドレスで既存ユーザーを検索
3. 既存ユーザーが存在すれば返す
4. 存在しなければ新規ユーザーを作成して保存
5. ユーザーを返す
"""

from app.domain.user import User
from app.domain.user_repository import UserRepository


class GoogleOAuthService:
    """Google OAuth認証のビジネスロジックを担当

    【ビジネスロジックとは？】
    「このアプリ独自のルール」のこと。
    - Googleから取得したユーザー情報でユーザーを作成/更新
    - 既存ユーザーの場合は既存ユーザーを返す
    これらは「OAuth認証サービス」なら必須のルール。

    【なぜUserやRepositoryと分ける？】
    役割を分けると変更しやすくなるから：
    - User: データの形を変えたい → user.pyだけ変更
    - Repository: 保存先を変えたい → repositoryだけ変更
    - Service: ルールを変えたい → serviceだけ変更

    これを「関心の分離」と言います。
    """

    def __init__(self, repository: UserRepository):
        """サービスを初期化する

        【なぜ__init__で受け取る？】
        これを「依存性注入（DI）」と言います。

        【依存性注入のメリット】
        テストのとき、本物のデータベースの代わりに
        「テスト用の偽物」を渡せます。
        本番→PostgreSQL、テスト→メモリ
        同じコードで両方動きます。

        Args:
            repository: ユーザーを検索・保存するリポジトリ
        """
        self._repository = repository

    def authenticate(self, google_user_info: dict) -> User:
        """Googleユーザー情報で認証し、ユーザーを作成または取得する

        【処理の流れ】
        1. Googleユーザー情報からemailを取得
        2. emailが存在しない場合 → エラー
        3. 既存ユーザーを検索
        4. 既存ユーザーが存在すれば返す
        5. 存在しなければ新規ユーザーを作成して保存
        6. ユーザーを返す

        【なぜOAuth認証でパスワードが必要？】
        現在のUserエンティティはhashed_passwordが必須のため、
        OAuth認証で作成されるユーザーにもダミーのパスワードを設定します。
        将来的には、OAuth認証ユーザーはパスワード不要にする設計変更が可能です。

        Args:
            google_user_info: Googleから取得したユーザー情報
                - email: メールアドレス（必須）
                - name: ユーザー名（任意）
                - sub: GoogleユーザーID（任意）

        Returns:
            作成または取得したUserオブジェクト

        Raises:
            ValueError: emailが欠けている場合
        """
        # ステップ1: emailの取得と検証
        email = google_user_info.get("email")
        if not email:
            raise ValueError("Email is required in google_user_info")

        # ステップ2: 既存ユーザーを検索
        existing_user = self._repository.find_by_email(email)
        if existing_user:
            # 既存ユーザーが存在すれば返す
            return existing_user

        # ステップ3: 新規ユーザーを作成
        # OAuth認証ではパスワードがないため、ダミーのパスワードを設定
        # 将来的には、OAuth認証ユーザーはパスワード不要にする設計変更が可能
        dummy_password = "oauth_user_no_password"
        user = User(
            email=email,
            hashed_password=dummy_password
        )

        # ステップ4: リポジトリに保存
        saved_user = self._repository.save(user)

        # ステップ5: 保存されたユーザーを返す
        return saved_user

