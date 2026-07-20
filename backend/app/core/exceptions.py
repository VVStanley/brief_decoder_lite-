import uuid


class BriefDecoderError(Exception):
    """Base exception for AI Brief Decoder Lite."""

    pass


class BriefNotFoundError(BriefDecoderError):
    """Raised when a brief cannot be found."""

    def __init__(self, brief_id: str | uuid.UUID) -> None:
        self.brief_id = brief_id
        super().__init__(f"Brief '{brief_id}' not found.")


class RepositoryContextError(BriefDecoderError):
    """Raised when a repository method is called outside of its context manager."""

    def __init__(self, message: str = "Repository context not entered") -> None:
        super().__init__(message)


class BriefInputValidationError(BriefDecoderError, ValueError):
    """Raised when brief input text fails validation (spam, gibberish, lack of words)."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
