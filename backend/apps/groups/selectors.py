from django.db.models import QuerySet, Count

from .models import GroupType, Group


def get_all_group_types(only_active: bool = True) -> QuerySet[GroupType]:
    """Barcha guruh turlarini olish"""
    qs = GroupType.objects.all()
    if only_active:
        qs = qs.filter(is_active=True)
    return qs


def get_group_type_by_id(group_type_id: int) -> GroupType | None:
    """ID bo'yicha guruh turini olish"""
    try:
        return GroupType.objects.get(id=group_type_id)
    except GroupType.DoesNotExist:
        return None


def get_group_type_by_slug(slug: str) -> GroupType | None:
    """Slug bo'yicha guruh turini olish"""
    try:
        return GroupType.objects.get(slug=slug)
    except GroupType.DoesNotExist:
        return None


def get_all_groups(only_active: bool = True) -> QuerySet[Group]:
    """Barcha guruhlarni olish"""
    qs = Group.objects.select_related('group_type')
    if only_active:
        qs = qs.filter(is_active=True)
    return qs


def get_groups_by_type(group_type_id: int, only_active: bool = True) -> QuerySet[Group]:
    """Guruh turi bo'yicha guruhlarni olish"""
    qs = Group.objects.filter(group_type_id=group_type_id)
    if only_active:
        qs = qs.filter(is_active=True)
    return qs.select_related('group_type')


def get_group_by_id(group_id: int) -> Group | None:
    """ID bo'yicha guruhni olish"""
    try:
        return Group.objects.select_related('group_type').get(id=group_id)
    except Group.DoesNotExist:
        return None


def get_group_by_slug(slug: str) -> Group | None:
    """Slug bo'yicha guruhni olish"""
    try:
        return Group.objects.select_related('group_type').get(slug=slug)
    except Group.DoesNotExist:
        return None


def get_groups_with_student_count() -> QuerySet[Group]:
    """Guruhlarni o'quvchilar soni bilan olish"""
    return Group.objects.filter(
        is_active=True
    ).select_related(
        'group_type'
    ).annotate(
        student_count=Count('students', filter=models.Q(students__is_active=True))
    )
