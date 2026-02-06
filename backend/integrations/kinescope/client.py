"""
Kinescope API Client

Kinescope - video hosting va DRM himoyasi bilan stream qilish xizmati.
API dokumentatsiyasi: https://kinescope.io/dev/api/

Asosiy funksiyalar:
- Video ma'lumotlarini olish (davomiylik, thumbnail, va h.k.)
- Embed URL generatsiya qilish
- DRM himoyalangan player olish
"""

import httpx
from typing import Optional
from dataclasses import dataclass
from django.conf import settings


@dataclass
class VideoInfo:
    """Video haqida ma'lumot"""
    id: str
    title: str
    description: str
    duration: int  # sekundlarda
    thumbnail_url: str
    embed_url: str
    status: str  # 'done', 'processing', 'error'


class KinescopeClient:
    """Kinescope API client"""

    BASE_URL = "https://api.kinescope.io/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'KINESCOPE_API_KEY', '')
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _make_request(self, method: str, endpoint: str, **kwargs) -> dict | None:
        """API ga so'rov yuborish"""
        url = f"{self.BASE_URL}{endpoint}"

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Kinescope API error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"Kinescope request error: {e}")
            return None

    def get_video(self, video_id: str) -> Optional[VideoInfo]:
        """Video ma'lumotlarini olish"""
        data = self._make_request("GET", f"/videos/{video_id}")

        if not data or 'data' not in data:
            return None

        video = data['data']

        return VideoInfo(
            id=video.get('id', ''),
            title=video.get('title', ''),
            description=video.get('description', ''),
            duration=video.get('duration', 0),
            thumbnail_url=video.get('poster', {}).get('url', ''),
            embed_url=f"https://kinescope.io/embed/{video_id}",
            status=video.get('status', 'unknown')
        )

    def get_video_duration(self, video_id: str) -> int:
        """Video davomiyligini olish (sekundlarda)"""
        video = self.get_video(video_id)
        return video.duration if video else 0

    def get_embed_code(
            self,
            video_id: str,
            autoplay: bool = False,
            loop: bool = False,
            muted: bool = False,
            controls: bool = True
    ) -> str:
        """Embed iframe kodi generatsiya qilish"""
        params = []
        if autoplay:
            params.append("autoplay=1")
        if loop:
            params.append("loop=1")
        if muted:
            params.append("muted=1")
        if not controls:
            params.append("controls=0")

        query_string = "&".join(params)
        url = f"https://kinescope.io/embed/{video_id}"
        if query_string:
            url += f"?{query_string}"

        return f'''<iframe 
    src="{url}" 
    allow="autoplay; fullscreen; picture-in-picture; encrypted-media; gyroscope; accelerometer; clipboard-write;" 
    frameborder="0" 
    allowfullscreen
    style="width: 100%; height: 100%;"
></iframe>'''

    def list_videos(self, project_id: Optional[str] = None, page: int = 1, per_page: int = 20) -> list[VideoInfo]:
        """Videolar ro'yxatini olish"""
        params = {"page": page, "per_page": per_page}
        if project_id:
            params["project_id"] = project_id

        data = self._make_request("GET", "/videos", params=params)

        if not data or 'data' not in data:
            return []

        videos = []
        for video in data['data']:
            videos.append(VideoInfo(
                id=video.get('id', ''),
                title=video.get('title', ''),
                description=video.get('description', ''),
                duration=video.get('duration', 0),
                thumbnail_url=video.get('poster', {}).get('url', ''),
                embed_url=f"https://kinescope.io/embed/{video.get('id', '')}",
                status=video.get('status', 'unknown')
            ))

        return videos


# Global client instance
kinescope_client = KinescopeClient()
