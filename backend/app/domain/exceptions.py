"""カスタム例外クラス

【なぜこのファイルが必要？】
エラーハンドリングを統一するため。
各エラーの種類に応じた適切なHTTPステータスコードを設定できる。

【エラーの分類】
- BusinessError: ビジネスルール違反（400番台）
- ValidationError: バリデーションエラー（400）
- AuthenticationError: 認証エラー（401）
- NotFoundError: リソース未検出（404）
"""


class BusinessError(Exception):
    """ビジネスルール違反エラー
    
    例：既に登録済みのメールアドレスで登録しようとした
    """
    status_code = 400

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ValidationError(Exception):
    """バリデーションエラー
    
    例：無効なメールアドレス形式、空のパスワード
    """
    status_code = 400

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class AuthenticationError(Exception):
    """認証エラー
    
    例：間違ったパスワード、無効なトークン
    """
    status_code = 401

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(Exception):
    """リソース未検出エラー
    
    例：存在しないユーザーIDで検索した
    """
    status_code = 404

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def convert_exception_to_http_status(exception: Exception) -> int:
    """例外をHTTPステータスコードに変換する
    
    Args:
        exception: カスタム例外オブジェクト
        
    Returns:
        HTTPステータスコード
    """
    if hasattr(exception, "status_code"):
        return exception.status_code
    # カスタム例外でない場合は500を返す
    return 500


def format_error_response(exception: Exception) -> dict:
    """例外を統一されたエラーレスポンス形式に変換する
    
    Args:
        exception: カスタム例外オブジェクト
        
    Returns:
        統一されたエラーレスポンス形式の辞書
    """
    # エラーコードを生成（例外クラス名から）
    error_code = exception.__class__.__name__.upper()
    
    return {
        "error": {
            "code": error_code,
            "message": str(exception),
        }
    }

