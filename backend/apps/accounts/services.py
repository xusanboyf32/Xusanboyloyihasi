from django.conf import settings
from django.utils import timezone

from core.exceptions import UserNotFoundError, InvalidOTPError, OTPExpiredError
from core.utils import generate_otp, create_deep_link_token

from .models import User, OTP
from .selectors import get_user_by_phone, get_user_by_id, get_active_otp


def create_student(
        phone_number: str,
        full_name: str,
        group_id: int | None = None
) -> User:
    """Yangi o'quvchi yaratish"""
    return User.objects.create_user(
        phone_number=phone_number,
        full_name=full_name,
        group_id=group_id,
        role=User.Role.STUDENT
    )


def create_admin(
        phone_number: str,
        full_name: str,
        is_super: bool = False
) -> User:
    """Yangi admin yaratish"""
    return User.objects.create_user(
        phone_number=phone_number,
        full_name=full_name,
        role=User.Role.SUPER_ADMIN if is_super else User.Role.ADMIN
    )


def update_user(user: User, **kwargs) -> User:
    """User ma'lumotlarini yangilash"""
    allowed_fields = ['full_name', 'phone_number', 'group_id', 'is_active']

    for field, value in kwargs.items():
        if field in allowed_fields:
            setattr(user, field, value)

    user.save()
    return user


def set_telegram_chat_id(user_id: int, chat_id: int) -> User | None:
    """Userga Telegram chat ID biriktirish"""
    user = get_user_by_id(user_id)
    if not user:
        return None

    user.telegram_chat_id = chat_id
    user.save(update_fields=['telegram_chat_id', 'updated_at'])
    return user


def initiate_login(phone_number: str) -> dict:
    """
    Login jarayonini boshlash
    Returns: {'user_id': int, 'deep_link': str, 'masked_phone': str}
    """
    user = get_user_by_phone(phone_number)

    if not user:
        raise UserNotFoundError()

    deep_link_token = create_deep_link_token(user.id)
    bot_username = settings.TELEGRAM_BOT_USERNAME if hasattr(settings, 'TELEGRAM_BOT_USERNAME') else 'your_bot'
    deep_link = f"https://t.me/{bot_username}?start={deep_link_token}"

    from core.utils import mask_phone_number

    return {
        'user_id': user.id,
        'deep_link': deep_link,
        'masked_phone': mask_phone_number(phone_number)
    }


def create_otp_for_user(user_id: int) -> OTP:
    """User uchun OTP yaratish (bot tomonidan chaqiriladi)"""
    user = get_user_by_id(user_id)

    if not user:
        raise UserNotFoundError()

    expire_seconds = getattr(settings, 'OTP_EXPIRE_SECONDS', 30)
    return OTP.create_for_user(user, expire_seconds)


def verify_otp(user_id: int, code: str) -> User:
    """OTP kodni tekshirish va login qilish"""
    user = get_user_by_id(user_id)
    print(f"DEBUG: user_id={user_id}, code={code}, user={user}")

    if not user:
        raise UserNotFoundError()

    otp = get_active_otp(user)
    print(f"DEBUG: otp={otp}, otp.code={otp.code if otp else None}, otp.is_valid={otp.is_valid if otp else None}")

    if not otp:
        raise InvalidOTPError("Kod topilmadi. Qaytadan urinib ko'ring.")

    if not otp.is_valid:
        raise OTPExpiredError()

    if otp.code != code:
        raise InvalidOTPError("Kod noto'g'ri")

    # OTP ni ishlatilgan deb belgilash
    otp.is_used = True
    otp.save(update_fields=['is_used', 'updated_at'])

    return user