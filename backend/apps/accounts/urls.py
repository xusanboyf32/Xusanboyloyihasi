from django.urls import path

from . import views
from . import api

app_name = 'accounts'

urlpatterns = [
    # Auth views (web)
    path('login/', views.LoginView.as_view(), name='login'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify_otp'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # Internal API (bot uchun)
    path('api/internal/verify-deep-link/', api.VerifyDeepLinkAPI.as_view(), name='api_verify_deep_link'),
    path('api/internal/check-user/', api.CheckUserAPI.as_view(), name='api_check_user'),
    path('api/internal/resend-otp/', api.ResendOTPAPI.as_view(), name='api_resend_otp'),
]