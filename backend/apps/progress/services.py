from django.utils import timezone

from .models import UserProgress
from .selectors import get_user_progress


def update_video_progress(user_id: int, lesson_id: int, progress_seconds: int) -> UserProgress:
    """Video progress yangilash"""
    user_progress, created = UserProgress.objects.get_or_create(
        user_id=user_id,
        lesson_id=lesson_id
    )

    # Faqat oldinga yangilash (orqaga qaytarmaslik)
    if progress_seconds > user_progress.video_progress:
        user_progress.video_progress = progress_seconds
        user_progress.save(update_fields=['video_progress', 'updated_at'])

    return user_progress


def mark_lesson_completed(user_id: int, lesson_id: int) -> UserProgress:
    """Darsni tugatilgan deb belgilash"""
    user_progress, created = UserProgress.objects.get_or_create(
        user_id=user_id,
        lesson_id=lesson_id
    )

    if not user_progress.is_completed:
        user_progress.is_completed = True
        user_progress.completed_at = timezone.now()
        user_progress.save(update_fields=['is_completed', 'completed_at', 'updated_at'])

    return user_progress


def reset_progress(user_id: int, lesson_id: int) -> bool:
    """Progressni qaytadan boshlash"""
    progress = get_user_progress(user_id, lesson_id)
    if not progress:
        return False

    progress.video_progress = 0
    progress.is_completed = False
    progress.completed_at = None
    progress.save()
    return True