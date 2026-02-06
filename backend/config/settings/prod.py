from .base import *

DEBUG = False

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# CSRF trusted origins bu shu domendan POST kelsa ishonchli deyli qolganiga error beradi
# CSRF trusted origins
# CSRF_TRUSTED_ORIGINS = [
#     'https://courses.asliddin.me',
#     'https://www.courses.asliddin.me',
# ]

# ////////////////////////////////////
CSRF_TRUSTED_ORIGINS = [
    'https://eduagent.uz',
    'https://www.eduagent.uz',

    'http://eduagent.uz',            # ✅ HTTP ham (redirect uchun)
    'http://www.eduagent.uz',
]
# //////////////////////////////////////////

# HTTPS - nginx handles SSL redirect
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
