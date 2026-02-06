"""
Kinescope Services

Lesson model bilan integratsiya qilish uchun xizmatlar.
"""

from typing import Optional

from .client import kinescope_client, VideoInfo


def sync_video_info(lesson) -> bool:
    """
    Lesson uchun video ma'lumotlarini Kinescope dan olish va yangilash

    Args:
        lesson: Lesson model instance

    Returns:
        Muvaffaqiyatli yangilandi yoki yo'q
    """
    if not lesson.kinescope_video_id:
        return False

    video_info = kinescope_client.get_video(lesson.kinescope_video_id)

    if not video_info:
        return False

    # Video davomiyligini yangilash
    if video_info.duration > 0:
        lesson.video_duration = video_info.duration
        lesson.save(update_fields=['video_duration'])

    return True


def get_video_info(video_id: str) -> Optional[VideoInfo]:
    """
    Video haqida to'liq ma'lumot olish

    Args:
        video_id: Kinescope video ID

    Returns:
        VideoInfo yoki None
    """
    return kinescope_client.get_video(video_id)


def get_embed_code(video_id: str, **kwargs) -> str:
    """
    Video uchun embed kod olish

    Args:
        video_id: Kinescope video ID
        **kwargs: embed parametrlari (autoplay, loop, muted, controls)

    Returns:
        HTML iframe kodi
    """
    return kinescope_client.get_embed_code(video_id, **kwargs)


def get_secure_embed_url(video_id: str, user_id: int = None) -> str:
    """
    DRM himoyalangan embed URL generatsiya qilish

    Kinescope DRM xususiyatlari:
    - Video yuklab olishni bloklash
    - Screen recording himoyasi
    - Watermark qo'shish imkoni
    - Geo-blocking

    Args:
        video_id: Video ID
        user_id: Foydalanuvchi ID (watermark uchun)

    Returns:
        Secure embed URL
    """
    base_url = f"https://kinescope.io/embed/{video_id}"

    params = [
        "drm=1",  # DRM yoqish
        "download=0",  # Yuklab olishni o'chirish
    ]

    # User ID watermark uchun
    if user_id:
        params.append(f"watermark={user_id}")

    return f"{base_url}?{'&'.join(params)}"


def format_duration(seconds: int) -> str:
    """
    Sekundlarni o'qilishi oson formatga o'tkazish

    Args:
        seconds: Sekundlar soni

    Returns:
        "HH:MM:SS" yoki "MM:SS" formati
    """
    if seconds <= 0:
        return "00:00"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def validate_video_id(video_id: str) -> tuple[bool, str]:
    """
    Video ID to'g'riligini tekshirish

    Args:
        video_id: Tekshiriladigan video ID

    Returns:
        (is_valid, message)
    """
    if not video_id:
        return False, "Video ID kiritilmagan"

    if len(video_id) < 10:
        return False, "Video ID juda qisqa"

    # Kinescope dan tekshirish
    video_info = kinescope_client.get_video(video_id)

    if not video_info:
        return False, "Video topilmadi yoki API xatosi"

    if video_info.status == 'error':
        return False, "Video processing xatosi"

    if video_info.status == 'processing':
        return True, "Video hali qayta ishlanmoqda"

    return True, "Video tayyor"