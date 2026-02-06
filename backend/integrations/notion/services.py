"""
Notion Services

Lesson model bilan integratsiya qilish uchun xizmatlar.
"""

from typing import Optional
from django.core.cache import cache

from .client import notion_client, NotionPage

# Cache timeout (5 daqiqa)
CACHE_TIMEOUT = 300


def get_lesson_content(lesson) -> str:
    """
    Dars uchun Notion kontentini olish (cache bilan)

    Args:
        lesson: Lesson model instance

    Returns:
        HTML content string
    """
    if not lesson.notion_page_id:
        return ""

    # Cache dan tekshirish
    cache_key = f"notion_content_{lesson.notion_page_id}"
    cached_content = cache.get(cache_key)

    if cached_content is not None:
        return cached_content

    # Notion dan olish
    content = notion_client.get_page_content(lesson.notion_page_id)

    # Cache ga saqlash
    if content:
        cache.set(cache_key, content, CACHE_TIMEOUT)

    return content


def get_lesson_page_info(lesson) -> Optional[NotionPage]:
    """
    Dars uchun Notion sahifa ma'lumotlarini olish

    Args:
        lesson: Lesson model instance

    Returns:
        NotionPage yoki None
    """
    if not lesson.notion_page_id:
        return None

    return notion_client.get_page(lesson.notion_page_id)


def get_full_lesson_page(lesson) -> Optional[NotionPage]:
    """
    Dars uchun Notion sahifa to'liq ma'lumot (metadata + content)

    Args:
        lesson: Lesson model instance

    Returns:
        NotionPage with html_content
    """
    if not lesson.notion_page_id:
        return None

    # Cache dan tekshirish
    cache_key = f"notion_page_{lesson.notion_page_id}"
    cached_page = cache.get(cache_key)

    if cached_page is not None:
        return cached_page

    # Notion dan olish
    page = notion_client.get_full_page(lesson.notion_page_id)

    # Cache ga saqlash
    if page:
        cache.set(cache_key, page, CACHE_TIMEOUT)

    return page


def clear_lesson_cache(lesson) -> None:
    """
    Dars uchun Notion cache ni tozalash

    Args:
        lesson: Lesson model instance
    """
    if not lesson.notion_page_id:
        return

    cache.delete(f"notion_content_{lesson.notion_page_id}")
    cache.delete(f"notion_page_{lesson.notion_page_id}")


def validate_page_id(page_id: str) -> tuple[bool, str]:
    """
    Notion page ID to'g'riligini tekshirish

    Args:
        page_id: Tekshiriladigan page ID

    Returns:
        (is_valid, message)
    """
    if not page_id:
        return False, "Page ID kiritilmagan"

    # ID uzunligini tekshirish (32 yoki 36 belgi)
    clean_id = page_id.replace('-', '')
    if len(clean_id) != 32:
        return False, "Page ID noto'g'ri formatda"

    # Notion dan tekshirish
    page = notion_client.get_page(page_id)

    if not page:
        return False, "Sahifa topilmadi yoki API xatosi"

    return True, f"Sahifa topildi: {page.title}"


def format_page_url(page_id: str) -> str:
    """
    Notion sahifa URL yaratish

    Args:
        page_id: Page ID

    Returns:
        Notion URL
    """
    clean_id = page_id.replace('-', '')
    return f"https://notion.so/{clean_id}"