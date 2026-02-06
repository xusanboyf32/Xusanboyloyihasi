from django.db.models import QuerySet

from .models import UserProgress


def get_user_progress(user_id: int, lesson_id: int) -> UserProgress | None:
    """Userning dars progressini olish"""
    try:
        return UserProgress.objects.get(user_id=user_id, lesson_id=lesson_id)
    except UserProgress.DoesNotExist:
        return None


def get_all_user_progress(user_id: int) -> QuerySet[UserProgress]:
    """Userning barcha progressini olish"""
    return UserProgress.objects.filter(
        user_id=user_id
    ).select_related('lesson').order_by('lesson__order')


def get_user_current_lesson(user_id: int) -> int:
    """Userning hozirgi dars raqamini olish"""
    last_completed = UserProgress.objects.filter(
        user_id=user_id,
        is_completed=True
    ).select_related('lesson').order_by('-lesson__order').first()

    if last_completed:
        return last_completed.lesson.order + 1
    return 1


def is_lesson_completed(user_id: int, lesson_id: int) -> bool:
    """Dars tugatilganmi?"""
    progress = get_user_progress(user_id, lesson_id)
    return progress.is_completed if progress else False


def can_user_access_lesson(user, lesson) -> bool:
    """User bu darsga kira oladimi?"""
    from apps.courses.selectors import is_lesson_available_for_user

    # Avval jadval bo'yicha tekshirish
    if not is_lesson_available_for_user(lesson, user):
        return False

    # Birinchi dars - doim ochiq
    if lesson.order == 1:
        return True

    # Oldingi dars tugatilgan bo'lishi kerak
    from apps.courses.models import Lesson
    previous_lesson = Lesson.objects.filter(
        order=lesson.order - 1,
        is_active=True
    ).first()

    if not previous_lesson:
        return True

    return is_lesson_completed(user.id, previous_lesson.id)