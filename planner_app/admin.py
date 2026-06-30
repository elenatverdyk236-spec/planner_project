from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('date', 'text', 'is_done', 'created_at')
    list_filter = ('date', 'is_done')
    search_fields = ('text', 'description')