from django.urls import path
from . import views

urlpatterns = [
    path('', views.week_view, name='week_view'),          # главная страница
    path('add/', views.add_task, name='add_task'),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),# для описания задач
    path('toggle/<int:task_id>/', views.toggle_done, name='toggle_done'),
    path('signup/', views.signup, name='signup'),
]