import httpx
from config import BACKEND_URL, BOT_API_TOKEN


class BackendAPI:
    """Backend API bilan ishlash"""

    def __init__(self):
        self.base_url = BACKEND_URL
        self.headers = {
            'X-Bot-Token': BOT_API_TOKEN,
            'Content-Type': 'application/json'
        }

    async def verify_deep_link(self, token: str, chat_id: int, phone_number: str) -> dict | None:
        """
        Deep link tokenni tekshirish va OTP yaratish.
        """
        url = f"{self.base_url}/auth/api/internal/verify-deep-link/"

        print(f"DEBUG: token={token}, chat_id={chat_id}, phone={phone_number}")  # DEBUG

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    json={
                        'token': token,
                        'chat_id': chat_id,
                        'phone_number': phone_number
                    },
                    headers=self.headers
                )

                if response.status_code == 200:
                    return response.json()

                # Xatolik bo'lsa ham response ni qaytarish
                try:
                    return response.json()
                except:
                    return {'success': False, 'error': 'unknown'}
        except Exception as e:
            print(f"Backend API error: {e}")
            return None

    async def check_user_by_chat_id(self, chat_id: int) -> dict | None:
        """
        Chat ID bo'yicha foydalanuvchini tekshirish.

        Returns:
            {
                'exists': True,
                'phone_number': '+998901234567',
                'full_name': 'John Doe'
            }
            or None if not found
        """
        url = f"{self.base_url}/auth/api/internal/check-user/"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    json={'chat_id': chat_id},
                    headers=self.headers
                )

                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            print(f"Backend API error: {e}")
            return None

    async def resend_otp(self, chat_id: int) -> dict | None:
        """
        OTP qayta yuborish.

        Returns:
            {
                'success': True,
                'otp_code': '123456'
            }
            or None if failed
        """
        url = f"{self.base_url}/auth/api/internal/resend-otp/"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    json={'chat_id': chat_id},
                    headers=self.headers
                )

                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            print(f"Backend API error: {e}")
            return None


# Singleton instance
backend_api = BackendAPI()