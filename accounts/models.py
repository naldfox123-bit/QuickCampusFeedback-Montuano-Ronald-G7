from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "STUDENT", "Student"
        ADMIN = "ADMIN", "Administrator"

    email = models.EmailField("email address", unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    contact_number = models.CharField(max_length=20, blank=True)

    def save(self, *args, **kwargs):
        # Superusers created with createsuperuser are always Administrators.
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)
