from django.db import models
from django.contrib.auth.models import User   # импортируем модель пользователя

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # привязка к пользователю
    date = models.DateField()
    text = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.text[:30]}"