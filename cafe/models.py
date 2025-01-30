# users/models.py
from django.db import models


class User(models.Model):
    user_id = models.AutoField(primary_key=True)  # Auto-incrementing integer
    username = models.CharField(max_length=255)  # Username as varchar
    department = models.CharField(max_length=255)  # Department as varchar
    created_at = models.DateTimeField(
        auto_now_add=True
    )  # Automatically sets timestamp when the record is created
    updated_at = models.DateTimeField(
        auto_now=True
    )  # Automatically updates timestamp when the record is modified
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username


