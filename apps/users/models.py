from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    matricula = models.CharField(max_length=30, unique=True)
    schoolName = models.CharField(max_length=120)

    def __str__(self):
        return self.username
