"""
Notion API Client

Notion - dars materiallari, qo'shimcha resurslar saqlash uchun.
API dokumentatsiyasi: https://developers.notion.com/
"""

import httpx
from typing import Optional
from dataclasses import dataclass, field
from django.conf import settings


@dataclass
class NotionBlock:
    """Notion blok"""
    id: str
    type: str
    content: str
    children: list = field(default_factory=list)


@dataclass
class NotionPage:
    """Notion sahifa"""
    id: str
    title: str
    icon: str
    cover_url: str
    blocks: list[NotionBlock] = field(default_factory=list)
    html_content: str = ""


class NotionClient:
    """Notion API client"""

    BASE_URL = "https://api.notion.com/v1"
    NOTION_VERSION = "2022-06-28"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'NOTION_API_KEY', '')
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": self.NOTION_VERSION
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
            print(f"Notion API error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"Notion request error: {e}")
            return None

    def _extract_text(self, rich_text: list) -> str:
        """Rich text dan formatlangan HTML olish"""
        if not rich_text:
            return ""

        result = []
        for t in rich_text:
            text = t.get('plain_text', '')
            annotations = t.get('annotations', {})
            href = t.get('href')

            # HTML escape
            text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

            # Formatting qo'llash
            if annotations.get('code'):
                text = f'<code class="bg-gray-200 dark:bg-dark-600 px-1.5 py-0.5 rounded text-sm font-mono">{text}</code>'
            if annotations.get('bold'):
                text = f'<strong class="font-semibold">{text}</strong>'
            if annotations.get('italic'):
                text = f'<em>{text}</em>'
            if annotations.get('strikethrough'):
                text = f'<del class="text-gray-400">{text}</del>'
            if annotations.get('underline'):
                text = f'<u>{text}</u>'
            if href:
                text = f'<a href="{href}" class="text-primary-500 hover:text-primary-600 underline" target="_blank" rel="noopener">{text}</a>'

            # Color
            color = annotations.get('color', 'default')
            if color != 'default':
                color_classes = {
                    'gray': 'text-gray-500',
                    'brown': 'text-amber-700',
                    'orange': 'text-orange-500',
                    'yellow': 'text-yellow-500',
                    'green': 'text-green-500',
                    'blue': 'text-blue-500',
                    'purple': 'text-purple-500',
                    'pink': 'text-pink-500',
                    'red': 'text-red-500',
                    'gray_background': 'bg-gray-100 dark:bg-gray-800 px-1 rounded',
                    'brown_background': 'bg-amber-100 dark:bg-amber-900/30 px-1 rounded',
                    'orange_background': 'bg-orange-100 dark:bg-orange-900/30 px-1 rounded',
                    'yellow_background': 'bg-yellow-100 dark:bg-yellow-900/30 px-1 rounded',
                    'green_background': 'bg-green-100 dark:bg-green-900/30 px-1 rounded',
                    'blue_background': 'bg-blue-100 dark:bg-blue-900/30 px-1 rounded',
                    'purple_background': 'bg-purple-100 dark:bg-purple-900/30 px-1 rounded',
                    'pink_background': 'bg-pink-100 dark:bg-pink-900/30 px-1 rounded',
                    'red_background': 'bg-red-100 dark:bg-red-900/30 px-1 rounded',
                }
                if color in color_classes:
                    text = f'<span class="{color_classes[color]}">{text}</span>'

            result.append(text)

        return "".join(result)

    def _block_to_html(self, block: dict) -> str:
        """Notion blokni HTML ga aylantirish"""
        block_type = block.get('type', '')
        block_data = block.get(block_type, {})

        # Paragraph
        if block_type == 'paragraph':
            text = self._extract_text(block_data.get('rich_text', []))
            if not text:
                return '<p class="mb-4">&nbsp;</p>'
            return f'<p class="mb-4 text-gray-700 dark:text-gray-300 leading-relaxed">{text}</p>'

        # Headings
        if block_type == 'heading_1':
            text = self._extract_text(block_data.get('rich_text', []))
            return f'<h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-4 mt-8">{text}</h1>'

        if block_type == 'heading_2':
            text = self._extract_text(block_data.get('rich_text', []))
            return f'<h2 class="text-xl font-bold text-gray-900 dark:text-white mb-3 mt-6">{text}</h2>'

        if block_type == 'heading_3':
            text = self._extract_text(block_data.get('rich_text', []))
            return f'<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2 mt-5">{text}</h3>'

        # Bulleted list
        if block_type == 'bulleted_list_item':
            text = self._extract_text(block_data.get('rich_text', []))
            return f'<li class="text-gray-700 dark:text-gray-300">{text}</li>'

        # Numbered list
        if block_type == 'numbered_list_item':
            text = self._extract_text(block_data.get('rich_text', []))
            return f'<li class="text-gray-700 dark:text-gray-300">{text}</li>'

        # To-do / Checkbox
        if block_type == 'to_do':
            text = self._extract_text(block_data.get('rich_text', []))
            checked = block_data.get('checked', False)
            if checked:
                return f'<div class="flex items-start gap-3 mb-2"><span class="text-green-500 mt-0.5">✓</span><span class="line-through text-gray-400">{text}</span></div>'
            else:
                return f'<div class="flex items-start gap-3 mb-2"><span class="text-gray-400 mt-0.5">☐</span><span class="text-gray-700 dark:text-gray-300">{text}</span></div>'

        # Code block
        if block_type == 'code':
            text = self._extract_text(block_data.get('rich_text', []))
            language = block_data.get('language', 'plain text')
            caption = self._extract_text(block_data.get('caption', []))

            # Code uchun HTML escape qilmaslik kerak, _extract_text da qilingan
            code_text = ""
            for t in block_data.get('rich_text', []):
                code_text += t.get('plain_text', '')
            code_text = code_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

            caption_html = f'<div class="text-xs text-gray-400 mt-2">{caption}</div>' if caption else ''
            return f'''<div class="mb-4">
    <div class="bg-gray-900 rounded-xl overflow-hidden">
        <div class="flex items-center justify-between px-4 py-2 bg-gray-800">
            <span class="text-xs text-gray-400">{language}</span>
        </div>
        <pre class="p-4 overflow-x-auto"><code class="text-sm text-gray-100 font-mono">{code_text}</code></pre>
    </div>
    {caption_html}
</div>'''

        # Quote
        if block_type == 'quote':
            text = self._extract_text(block_data.get('rich_text', []))
            return f'<blockquote class="border-l-4 border-primary-500 pl-4 py-2 mb-4 text-gray-600 dark:text-gray-400 italic bg-gray-50 dark:bg-dark-700/50 rounded-r-lg">{text}</blockquote>'

        # Callout
        if block_type == 'callout':
            text = self._extract_text(block_data.get('rich_text', []))
            icon = ""
            icon_data = block_data.get('icon', {})
            if icon_data.get('type') == 'emoji':
                icon = icon_data.get('emoji', '💡')

            # Callout color
            color = block_data.get('color', 'gray_background')
            bg_classes = {
                'gray_background': 'bg-gray-100 dark:bg-gray-800',
                'brown_background': 'bg-amber-50 dark:bg-amber-900/20',
                'orange_background': 'bg-orange-50 dark:bg-orange-900/20',
                'yellow_background': 'bg-yellow-50 dark:bg-yellow-900/20',
                'green_background': 'bg-green-50 dark:bg-green-900/20',
                'blue_background': 'bg-blue-50 dark:bg-blue-900/20',
                'purple_background': 'bg-purple-50 dark:bg-purple-900/20',
                'pink_background': 'bg-pink-50 dark:bg-pink-900/20',
                'red_background': 'bg-red-50 dark:bg-red-900/20',
            }
            bg_class = bg_classes.get(color, 'bg-gray-100 dark:bg-gray-800')

            return f'''<div class="flex items-start gap-3 p-4 rounded-xl {bg_class} mb-4">
    <span class="text-xl flex-shrink-0">{icon}</span>
    <div class="text-gray-700 dark:text-gray-300 flex-1">{text}</div>
</div>'''

        # Divider
        if block_type == 'divider':
            return '<hr class="my-6 border-gray-200 dark:border-gray-700">'

        # Image
        if block_type == 'image':
            url = ""
            if block_data.get('type') == 'external':
                url = block_data.get('external', {}).get('url', '')
            elif block_data.get('type') == 'file':
                url = block_data.get('file', {}).get('url', '')

            caption = self._extract_text(block_data.get('caption', []))
            if url:
                caption_html = f'<figcaption class="text-center text-sm text-gray-500 mt-2">{caption}</figcaption>' if caption else ''
                return f'''<figure class="mb-4">
    <img src="{url}" alt="{caption}" class="rounded-xl w-full" loading="lazy">
    {caption_html}
</figure>'''

        # Video
        if block_type == 'video':
            url = ""
            if block_data.get('type') == 'external':
                url = block_data.get('external', {}).get('url', '')

            if url:
                # YouTube
                if 'youtube.com' in url or 'youtu.be' in url:
                    if 'v=' in url:
                        video_id = url.split('v=')[1].split('&')[0]
                    elif 'youtu.be/' in url:
                        video_id = url.split('youtu.be/')[1].split('?')[0]
                    else:
                        video_id = url.split('/')[-1]

                    return f'''<div class="aspect-video mb-4 rounded-xl overflow-hidden">
    <iframe src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen class="w-full h-full"></iframe>
</div>'''

                # Boshqa video
                return f'''<div class="mb-4">
    <video src="{url}" controls class="w-full rounded-xl"></video>
</div>'''

        # Bookmark
        if block_type == 'bookmark':
            url = block_data.get('url', '')
            caption = self._extract_text(block_data.get('caption', []))
            caption_html = f'<p class="text-sm text-gray-500 mt-1 truncate">{caption}</p>' if caption else ''
            return f'''<a href="{url}" target="_blank" rel="noopener" class="block p-4 rounded-xl bg-gray-50 dark:bg-dark-700 hover:bg-gray-100 dark:hover:bg-dark-600 mb-4 transition-colors border border-gray-200 dark:border-gray-700">
    <p class="text-primary-500 truncate text-sm">{url}</p>
    {caption_html}
</a>'''

        # Toggle
        if block_type == 'toggle':
            text = self._extract_text(block_data.get('rich_text', []))
            block_id = block.get('id', '')
            return f'''<details class="mb-4 group">
    <summary class="cursor-pointer p-4 rounded-xl bg-gray-50 dark:bg-dark-700 hover:bg-gray-100 dark:hover:bg-dark-600 transition-colors font-medium text-gray-900 dark:text-white list-none flex items-center gap-2">
        <svg class="w-4 h-4 transition-transform group-open:rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
        {text}
    </summary>
    <div class="pl-6 pt-2 text-gray-600 dark:text-gray-400" data-toggle-id="{block_id}"><!-- children --></div>
</details>'''

        # Table
        if block_type == 'table':
            return '<div class="overflow-x-auto mb-4" data-table="true"><!-- table content --></div>'

        if block_type == 'table_row':
            cells = block_data.get('cells', [])
            cells_html = "".join([f'<td class="px-4 py-2 border border-gray-200 dark:border-gray-700">{self._extract_text(cell)}</td>' for cell in cells])
            return f'<tr>{cells_html}</tr>'

        # Embed
        if block_type == 'embed':
            url = block_data.get('url', '')
            return f'''<div class="mb-4 rounded-xl overflow-hidden">
    <iframe src="{url}" class="w-full h-96 border-0" allowfullscreen></iframe>
</div>'''

        # PDF
        if block_type == 'pdf':
            url = ""
            if block_data.get('type') == 'external':
                url = block_data.get('external', {}).get('url', '')
            elif block_data.get('type') == 'file':
                url = block_data.get('file', {}).get('url', '')

            if url:
                return f'''<div class="mb-4">
    <a href="{url}" target="_blank" class="flex items-center gap-3 p-4 rounded-xl bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors">
        <svg class="w-8 h-8 text-red-500" fill="currentColor" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm-1 2l5 5h-5V4zM9.5 11c.83 0 1.5.67 1.5 1.5v1c0 .83-.67 1.5-1.5 1.5H9v2H7.5v-6h2zm3.5 0h2c.83 0 1.5.67 1.5 1.5v3c0 .83-.67 1.5-1.5 1.5h-2v-6zm-3 1.5v1h.5v-1H10zm3 0v3h.5v-3H13z"/></svg>
        <span class="text-red-600 dark:text-red-400 font-medium">PDF faylni ko'rish</span>
    </a>
</div>'''

        # File
        if block_type == 'file':
            url = ""
            name = ""
            if block_data.get('type') == 'external':
                url = block_data.get('external', {}).get('url', '')
            elif block_data.get('type') == 'file':
                url = block_data.get('file', {}).get('url', '')
            name = block_data.get('name', 'Fayl')

            if url:
                return f'''<div class="mb-4">
    <a href="{url}" target="_blank" download class="flex items-center gap-3 p-4 rounded-xl bg-gray-50 dark:bg-dark-700 hover:bg-gray-100 dark:hover:bg-dark-600 transition-colors">
        <svg class="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
        <span class="text-gray-700 dark:text-gray-300">{name}</span>
    </a>
</div>'''

        # Equation (math)
        if block_type == 'equation':
            expression = block_data.get('expression', '')
            return f'<div class="mb-4 p-4 bg-gray-50 dark:bg-dark-700 rounded-xl text-center font-mono text-gray-700 dark:text-gray-300">{expression}</div>'

        # Column list va column - skip
        if block_type in ['column_list', 'column']:
            return ''

        return ""

    def get_page(self, page_id: str) -> Optional[NotionPage]:
        """Sahifa ma'lumotlarini olish"""
        # Page ID formatlash
        clean_id = page_id.replace('-', '')
        if len(clean_id) == 32:
            page_id = f"{clean_id[:8]}-{clean_id[8:12]}-{clean_id[12:16]}-{clean_id[16:20]}-{clean_id[20:]}"

        page_data = self._make_request("GET", f"/pages/{page_id}")

        if not page_data:
            return None

        # Title olish
        title = ""
        properties = page_data.get('properties', {})
        for prop in properties.values():
            if prop.get('type') == 'title':
                title = self._extract_text(prop.get('title', []))
                break

        # Icon
        icon = ""
        icon_data = page_data.get('icon', {})
        if icon_data.get('type') == 'emoji':
            icon = icon_data.get('emoji', '')

        # Cover
        cover_url = ""
        cover_data = page_data.get('cover', {})
        if cover_data:
            if cover_data.get('type') == 'external':
                cover_url = cover_data.get('external', {}).get('url', '')
            elif cover_data.get('type') == 'file':
                cover_url = cover_data.get('file', {}).get('url', '')

        return NotionPage(id=page_id, title=title, icon=icon, cover_url=cover_url)

    def get_page_content(self, page_id: str) -> str:
        """Sahifa kontentini HTML formatda olish"""
        clean_id = page_id.replace('-', '')
        if len(clean_id) == 32:
            page_id = f"{clean_id[:8]}-{clean_id[8:12]}-{clean_id[12:16]}-{clean_id[16:20]}-{clean_id[20:]}"

        blocks_data = self._make_request("GET", f"/blocks/{page_id}/children")

        if not blocks_data or 'results' not in blocks_data:
            return ""

        html_parts = []
        current_list_type = None
        list_items = []

        for block in blocks_data['results']:
            block_type = block.get('type', '')

            # List elementlarini guruhlash
            if block_type == 'bulleted_list_item':
                if current_list_type != 'bulleted':
                    if list_items:
                        tag = 'ul' if current_list_type == 'bulleted' else 'ol'
                        list_class = 'list-disc' if current_list_type == 'bulleted' else 'list-decimal'
                        html_parts.append(f'<{tag} class="mb-4 ml-6 space-y-1 {list_class}">{"".join(list_items)}</{tag}>')
                        list_items = []
                    current_list_type = 'bulleted'
                list_items.append(self._block_to_html(block))

            elif block_type == 'numbered_list_item':
                if current_list_type != 'numbered':
                    if list_items:
                        tag = 'ul' if current_list_type == 'bulleted' else 'ol'
                        list_class = 'list-disc' if current_list_type == 'bulleted' else 'list-decimal'
                        html_parts.append(f'<{tag} class="mb-4 ml-6 space-y-1 {list_class}">{"".join(list_items)}</{tag}>')
                        list_items = []
                    current_list_type = 'numbered'
                list_items.append(self._block_to_html(block))

            else:
                # Oldingi listni yopish
                if list_items:
                    tag = 'ul' if current_list_type == 'bulleted' else 'ol'
                    list_class = 'list-disc' if current_list_type == 'bulleted' else 'list-decimal'
                    html_parts.append(f'<{tag} class="mb-4 ml-6 space-y-1 {list_class}">{"".join(list_items)}</{tag}>')
                    list_items = []
                    current_list_type = None

                html = self._block_to_html(block)
                if html:
                    html_parts.append(html)

        # Oxirgi listni yopish
        if list_items:
            tag = 'ul' if current_list_type == 'bulleted' else 'ol'
            list_class = 'list-disc' if current_list_type == 'bulleted' else 'list-decimal'
            html_parts.append(f'<{tag} class="mb-4 ml-6 space-y-1 {list_class}">{"".join(list_items)}</{tag}>')

        return "\n".join(html_parts)

    def get_full_page(self, page_id: str) -> Optional[NotionPage]:
        """Sahifa metadata va kontentini birga olish"""
        page = self.get_page(page_id)
        if not page:
            return None
        page.html_content = self.get_page_content(page_id)
        return page


# Global client instance
notion_client = NotionClient()