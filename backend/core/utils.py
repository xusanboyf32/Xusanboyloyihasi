import random
import string
import hashlib
import hmac
from django.conf import settings
from django.utils import timezone


def generate_otp(length: int = 6) -> str:
    """Tasodifiy OTP kod generatsiya qilish"""
    return ''.join(random.choices(string.digits, k=length))


def generate_token(length: int = 32) -> str:
    """Tasodifiy token generatsiya qilish"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def create_deep_link_token(user_id: int) -> str:
    """
    User ID ni xavfsiz tokenga aylantirish (Telegram deep link uchun)
    Token = user_id + timestamp + signature
    """
    timestamp = int(timezone.now().timestamp())
    data = f"{user_id}:{timestamp}"

    signature = hmac.new(
        settings.SECRET_KEY.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()[:16]

    return f"{user_id}_{timestamp}_{signature}"


def verify_deep_link_token(token: str, max_age_seconds: int = 300) -> int | None:
    """
    Deep link tokenni tekshirish va user_id qaytarish
    max_age_seconds: token necha sekund valid (default 5 minut)
    """
    try:
        parts = token.split('_')
        if len(parts) != 3:
            return None

        user_id, timestamp, signature = parts
        user_id = int(user_id)
        timestamp = int(timestamp)

        # Vaqtni tekshirish
        current_time = int(timezone.now().timestamp())
        if current_time - timestamp > max_age_seconds:
            return None

        # Signature tekshirish
        data = f"{user_id}:{timestamp}"
        expected_signature = hmac.new(
            settings.SECRET_KEY.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()[:16]

        if not hmac.compare_digest(signature, expected_signature):
            return None

        return user_id
    except (ValueError, AttributeError):
        return None


def mask_phone_number(phone: str) -> str:
    """Telefon raqamni maskalash: +998901234567 -> +998***4567"""
    if len(phone) < 8:
        return phone
    return phone[:4] + '***' + phone[-4:]