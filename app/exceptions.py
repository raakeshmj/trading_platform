class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class InsufficientFundsError(AppError):
    def __init__(self, message="Insufficient funds"):
        super().__init__(message, status_code=400)

class InsufficientHoldingsError(AppError):
    def __init__(self, message="Insufficient holdings"):
        super().__init__(message, status_code=400)

class InstrumentNotFoundError(AppError):
    def __init__(self, message="Instrument not found"):
        super().__init__(message, status_code=404)

class OrderNotFoundError(AppError):
    def __init__(self, message="Order not found"):
        super().__init__(message, status_code=404)
