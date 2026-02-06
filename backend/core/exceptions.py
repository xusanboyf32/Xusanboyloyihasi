
class BaseAPIException(Exception):
    """Base exception for API errors"""
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class UserNotFoundError(BaseAPIException):
    """User topilmadi"""
    def __init__(self, message: str = "Foydalanuvchi topilmadi"):
        super().__init__(message, code="user_not_found")


class InvalidOTPError(BaseAPIException):
    """OTP noto'g'ri yoki eskirgan"""
    def __init__(self, message: str = "Kod noto'g'ri yoki eskirgan"):
        super().__init__(message, code="invalid_otp")


class OTPExpiredError(BaseAPIException):
    """OTP muddati tugagan"""
    def __init__(self, message: str = "Kod muddati tugagan"):
        super().__init__(message, code="otp_expired")


class AccessDeniedError(BaseAPIException):
    """Ruxsat yo'q"""
    def __init__(self, message: str = "Ruxsat berilmagan"):
        super().__init__(message, code="access_denied")


class LessonLockedError(BaseAPIException):
    """Dars hali ochilmagan"""
    def __init__(self, message: str = "Bu dars hali sizga ochilmagan"):
        super().__init__(message, code="lesson_locked")

