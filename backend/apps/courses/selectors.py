from django.db.models import QuerySet
from django.utils import timezone

from .models import Lesson, LessonSchedule


def get_all_lessons(only_active: bool = True) -> QuerySet[Lesson]:
    """Barcha darslarni olish"""
    qs = Lesson.objects.all()
    if only_active:
        qs = qs.filter(is_active=True)
    return qs.order_by('order')


def get_lesson_by_id(lesson_id: int) -> Lesson | None:
    """ID bo'yicha darsni olish"""
    try:
        return Lesson.objects.get(id=lesson_id)
    except Lesson.DoesNotExist:
        return None


def get_lesson_by_slug(slug: str) -> Lesson | None:
    """Slug bo'yicha darsni olish"""
    try:
        return Lesson.objects.get(slug=slug)
    except Lesson.DoesNotExist:
        return None


def get_available_lessons_for_group_type(group_type_id: int) -> QuerySet[Lesson]:
    """Guruh turi uchun ochiq darslarni olish"""
    now = timezone.now()

    available_lesson_ids = LessonSchedule.objects.filter(
        group_type_id=group_type_id,
        available_from__lte=now
    ).values_list('lesson_id', flat=True)

    return Lesson.objects.filter(
        id__in=available_lesson_ids,
        is_active=True
    ).order_by('order')


def get_lesson_schedule(lesson_id: int, group_type_id: int) -> LessonSchedule | None:
    """Dars jadvalini olish"""
    try:
        return LessonSchedule.objects.get(
            lesson_id=lesson_id,
            group_type_id=group_type_id
        )
    except LessonSchedule.DoesNotExist:
        return None




def is_lesson_available_for_user(lesson: Lesson, user) -> bool:
    """Dars userga ochiqmi?"""
    if not user.group:
        return False

    schedule = get_lesson_schedule(lesson.id, user.group.group_type_id)

    if not schedule:
        return False

    return schedule.available_from <= timezone.now()
