from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

from core.mixins import TimeStampMixin


class UserManager(BaseUserManager):
    def create_user(self, phone_number, full_name, **extra_fields):
        if not phone_number:
            raise ValueError("Telefon raqam kiritilishi shart")

        user = self.model(
            phone_number=phone_number,
            full_name=full_name,
            **extra_fields
        )
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.SUPER_ADMIN)

        user = self.model(
            phone_number=phone_number,
            full_name=full_name,
            **extra_fields
        )
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin, TimeStampMixin):
    """Custom User model"""

    class Role(models.TextChoices):
        STUDENT = 'student', 'Oquvchi'
        ADMIN = 'admin', 'Admin'
        SUPER_ADMIN = 'super_admin', 'Super Admin'

    phone_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Telefon raqam"
    )
    full_name = models.CharField(
        max_length=255,
        verbose_name="To'liq ism"
    )
    telegram_chat_id = models.BigIntegerField(
        null=True,
        blank=True,
        unique=True,
        verbose_name="Telegram Chat ID"
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name="Role"
    )
    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name="Guruh"
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"

    @property
    def is_student(self) -> bool:
        return self.role == self.Role.STUDENT

    @property
    def is_admin(self) -> bool:
        return self.role in [self.Role.ADMIN, self.Role.SUPER_ADMIN]

    @property
    def is_super_admin(self) -> bool:
        return self.role == self.Role.SUPER_ADMIN


class OTP(TimeStampMixin):
    """OTP kodlar uchun model"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='otps'
    )
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = "OTP"
        verbose_name_plural = "OTP kodlar"
        ordering = ['-created_at']

    def __str__(self):
        return f"OTP for {self.user.phone_number}"

    @property
    def is_valid(self) -> bool:
        """OTP hali yaroqlimi?"""
        return not self.is_used and timezone.now() < self.expires_at

    @classmethod
    def create_for_user(cls, user: User, expire_seconds: int = 30) -> 'OTP':
        """User uchun yangi OTP yaratish"""
        from core.utils import generate_otp

        # Eski OTPlarni bekor qilish
        cls.objects.filter(user=user, is_used=False).update(is_used=True)

        return cls.objects.create(
            user=user,
            code=generate_otp(),
            expires_at=timezone.now() + timezone.timedelta(seconds=expire_seconds)
        )