from django.utils.text import slugify

from .models import GroupType, Group
from .selectors import get_group_type_by_id, get_group_by_id


def create_group_type(name: str, description: str = '') -> GroupType:
    """Yangi guruh turi yaratish"""
    return GroupType.objects.create(
        name=name,
        description=description,
        slug=slugify(name)
    )


def update_group_type(group_type_id: int, **kwargs) -> GroupType | None:
    """Guruh turini yangilash"""
    group_type = get_group_type_by_id(group_type_id)
    if not group_type:
        return None

    allowed_fields = ['name', 'description', 'is_active']

    for field, value in kwargs.items():
        if field in allowed_fields:
            setattr(group_type, field, value)

    if 'name' in kwargs:
        group_type.slug = slugify(kwargs['name'])

    group_type.save()
    return group_type


def delete_group_type(group_type_id: int) -> bool:
    """Guruh turini o'chirish (soft delete)"""
    group_type = get_group_type_by_id(group_type_id)
    if not group_type:
        return False

    group_type.is_active = False
    group_type.save(update_fields=['is_active', 'updated_at'])
    return True


def create_group(name: str, group_type_id: int, description: str = '') -> Group:
    """Yangi guruh yaratish"""
    group_type = get_group_type_by_id(group_type_id)

    return Group.objects.create(
        name=name,
        group_type=group_type,
        description=description,
        slug=slugify(f"{group_type.name}-{name}")
    )


def update_group(group_id: int, **kwargs) -> Group | None:
    """Guruhni yangilash"""
    group = get_group_by_id(group_id)
    if not group:
        return None

    allowed_fields = ['name', 'description', 'is_active', 'group_type_id']

    for field, value in kwargs.items():
        if field in allowed_fields:
            setattr(group, field, value)

    group.save()
    return group


def delete_group(group_id: int) -> bool:
    """Guruhni o'chirish (soft delete)"""
    group = get_group_by_id(group_id)
    if not group:
        return False

    group.is_active = False
    group.save(update_fields=['is_active', 'updated_at'])
    return True