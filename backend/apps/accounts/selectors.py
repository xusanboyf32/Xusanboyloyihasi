from django.db.models import QuerySet

from .models import User, OTP


def get_user_by_phone(phone_number: str) -> User | None:
    """Telefon raqam bo'yicha user topish"""
    try:
        return User.objects.get(phone_number=phone_number, is_active=True)
    except User.DoesNotExist:
        return None


def get_user_by_id(user_id: int) -> User | None:
    """ID bo'yicha user topish"""
    try:
        return User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist:
        return None


def get_user_by_telegram_chat_id(chat_id: int) -> User | None:
    """Telegram chat ID bo'yicha user topish"""
    try:
        return User.objects.get(telegram_chat_id=chat_id, is_active=True)
    except User.DoesNotExist:
        return None


def get_active_otp(user: User) -> OTP | None:
    """Userning faol OTP sini olish"""
    return OTP.objects.filter(
        user=user,
        is_used=False
    ).order_by('-created_at').first()


def get_all_admins() -> QuerySet[User]:
    """Barcha adminlarni olish"""
    return User.objects.filter(
        role__in=[User.Role.ADMIN, User.Role.SUPER_ADMIN],
        is_active=True
    )


def get_students_by_group(group_id: int) -> QuerySet[User]:
    """Guruhdagi o'quvchilarni olish"""
    return User.objects.filter(
        group_id=group_id,
        role=User.Role.STUDENT,
        is_active=True
    ).select_related('group')