"""SessionStoreインターフェース

【なぜこのファイルが必要？】
セッション情報を「どこかに保存する」ためのルールブックです。

例えるなら、図書館の「貸し出しカード管理システム」のようなものです：
- 「保存する」→ 貸し出しカードを記録
- 「取得する」→ 貸し出しカードを確認
- 「削除する」→ 返却時にカードを削除

【なぜ「抽象クラス」にする？】
実際の保存先はいろいろありえます：
- Redis（本番環境）
- メモリ（テスト環境）
- PostgreSQL（代替案）

でも、使う側は「保存先がどこか」を気にしなくていい。
「saveを呼べば保存される」ことだけ知っていればOK。
これを「抽象化」と言います。
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class SessionStore(ABC):
    """セッションデータの保存・取得・削除を行うインターフェース

    【ABCとは？】
    Abstract Base Class（抽象基底クラス）の略。
    「このクラスは直接使えません。継承して使ってね」という意味。

    【@abstractmethodとは？】
    「このメソッドは必ず実装してね」という約束。
    実装しないとエラーになるので、実装忘れを防げます。

    【なぜインターフェースを使う？】
    LoginServiceは「セッションを保存する機能」が欲しいだけ。
    保存先がRedisかメモリかは関係ない。
    インターフェースを使うと、保存先を後から自由に変えられます。
    """

    @abstractmethod
    def save(self, session_id: str, data: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """セッションを保存する

        Args:
            session_id: セッションID（一意の識別子）
            data: 保存するデータ（辞書形式）
            ttl: 有効期限（秒単位）。Noneの場合は無期限

        【なぜttlをオプションにする？】
        セッションには有効期限を設定できるが、
        テストなどでは無期限でも問題ない場合がある。
        """
        pass

    @abstractmethod
    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """セッションを取得する

        Args:
            session_id: セッションID

        Returns:
            セッションデータ（辞書形式）。見つからない場合はNone

        【なぜNoneを返す可能性がある？】
        セッションが存在しない、または有効期限切れの場合があるから。
        """
        pass

    @abstractmethod
    def delete(self, session_id: str) -> None:
        """セッションを削除する

        Args:
            session_id: セッションID

        【なぜ削除が必要？】
        ログアウト時にセッションを無効化するため。
        """
        pass

