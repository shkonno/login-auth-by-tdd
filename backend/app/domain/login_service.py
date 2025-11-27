"""ログインサービス

【なぜこのファイルが必要？】
「ログイン」という作業の「手順書」です。

例えるなら、図書館の「会員カード確認マニュアル」のようなもの：
1. 会員カード（メールアドレス）を見せる
2. 暗証番号（パスワード）を入力
3. 正しければ入館証（JWTトークン）を発行

【なぜServiceという名前？】
プログラミングでは「何かの処理をまとめたもの」をServiceと呼びます。
- 登録Service（RegistrationService）
- ログインService（LoginService）
- 注文Service
など、機能ごとに分けると管理しやすくなります。
"""

from typing import Callable

from app.domain.password import verify_password
from app.domain.jwt import create_access_token


class LoginService:
    """ログインのビジネスロジックを担当

    【ビジネスロジックとは？】
    「このアプリ独自のルール」のこと。
    - メールアドレスとパスワードが一致するか確認
    - 正しければJWTトークンを発行
    これらは「ログインサービス」なら必須のルール。

    【なぜUserやRepositoryと分ける？】
    役割を分けると変更しやすくなるから：
    - User: データの形を変えたい → user.pyだけ変更
    - Repository: 保存先を変えたい → repositoryだけ変更
    - Service: ルールを変えたい → serviceだけ変更

    これを「関心の分離」と言います。
    """

    def __init__(
        self,
        repository,
        verifier: Callable[[str, str], bool] = verify_password,
        token_creator: Callable[[dict], str] = create_access_token
    ):
        """サービスを初期化する

        【なぜ__init__で受け取る？】
        これを「依存性注入（DI）」と言います。

        【依存性注入のメリット】
        テストのとき、本物のデータベースの代わりに
        「テスト用の偽物」を渡せます。
        本番→PostgreSQL、テスト→メモリ
        同じコードで両方動きます。

        【なぜverifierも受け取る？】
        本物のbcryptは遅い（1回0.1秒くらい）。
        テストで100回呼ぶと10秒かかってしまう。
        テスト用の高速な偽物を渡せるようにしています。

        Args:
            repository: ユーザーを検索するリポジトリ
            verifier: パスワード検証関数（デフォルト: verify_password）
            token_creator: JWT生成関数（デフォルト: create_access_token）
        """
        self._repository = repository
        self._verifier = verifier
        self._token_creator = token_creator

    def login(self, email: str, password: str) -> str:
        """ユーザーをログインさせる

        【処理の流れ】
        1. メールアドレスでユーザーを検索
        2. ユーザーが見つからない場合 → エラー
        3. パスワードを検証
        4. 検証失敗 → エラー
        5. 検証成功 → JWTトークンを生成して返す

        【なぜJWTトークンを返す？】
        トークンは「ログイン中」の証明書のようなもの。
        フロントエンドがこのトークンを持っていれば、
        保護されたページにアクセスできます。

        Args:
            email: ユーザーのメールアドレス
            password: ユーザーが入力したパスワード（平文）

        Returns:
            JWTトークン（文字列）

        Raises:
            ValueError: ユーザーが見つからない、またはパスワードが間違っている場合
        """
        # ステップ1: ユーザーを検索
        user = self._repository.find_by_email(email)
        if not user:
            raise ValueError("Invalid email or password")

        # ステップ1.5: ユーザーが有効かチェック
        # 【なぜis_activeをチェック？】
        # 退会したユーザーや、管理者によって無効化されたユーザーは
        # ログインできないようにするため。
        if not user.is_active:
            raise ValueError("Invalid email or password")

        # ステップ2: パスワードを検証
        if not self._verifier(password, user.hashed_password):
            raise ValueError("Invalid email or password")

        # ステップ3: JWTトークンを生成
        # 【なぜ{"sub": str(user.id)}？】
        # JWTの標準的なペイロード形式。
        # "sub"はSubject（誰のトークンか）を表します。
        # user.idを文字列に変換して含めます。
        token_data = {"sub": str(user.id)}
        token = self._token_creator(token_data)

        # ステップ4: トークンを返す
        return token

