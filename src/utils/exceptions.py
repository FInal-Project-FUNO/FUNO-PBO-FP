"""
Custom exceptions for the Funo game
"""

class FunoException(Exception):
    """Base exception for Funo game"""
    pass

class InvalidMoveError(FunoException):
    """Raised when a player makes an invalid move"""
    def __init__(self, message="Invalid move: card doesn't match main card"):
        self.message = message
        super().__init__(self.message)

class EmptyDeckError(FunoException):
    """Raised when deck is empty"""
    def __init__(self, message="Deck is empty"):
        self.message = message
        super().__init__(self.message)

class InvalidCardError(FunoException):
    """Raised when card is invalid"""
    def __init__(self, message="Invalid card"):
        self.message = message
        super().__init__(self.message)