import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Task

# Создаём логгер для текущего модуля
logger = logging.getLogger(__name__)


@login_required
def week_view(request):
    """
    Отображение недели с задачами текущего пользователя.
    """
    try:
        offset = int(request.GET.get('offset', 0))
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_week += timedelta(weeks=offset)

        days = []
        for i in range(7):
            day_date = start_of_week + timedelta(days=i)
            tasks = Task.objects.filter(user=request.user, date=day_date).order_by('created_at')
            days.append({'date': day_date, 'tasks': tasks})

        week_title = (
            f"{start_of_week.strftime('%d %B')} – "
            f"{(start_of_week + timedelta(days=6)).strftime('%d %B %Y')}"
        )

        context = {'days': days, 'week_title': week_title, 'offset': offset}

        # Логируем успешное открытие страницы
        logger.info(f"Пользователь {request.user.username} открыл неделю с offset={offset}")

        return render(request, 'planner_app/week.html', context)

    except Exception as e:
        # Логируем ошибку
        logger.error(f"Ошибка в week_view для пользователя {request.user.username}: {e}", exc_info=True)
        # Можно вернуть страницу с ошибкой или перенаправить
        return render(request, 'planner_app/week.html', {'days': [], 'week_title': 'Ошибка', 'offset': 0})


@login_required
def add_task(request):
    """
    Добавление новой задачи.
    """
    if request.method == 'POST':
        date_str = request.POST.get('date')
        text = request.POST.get('text')
        if date_str and text:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                Task.objects.create(user=request.user, date=date, text=text)
                logger.info(f"Пользователь {request.user.username} добавил задачу '{text}' на {date}")
            except Exception as e:
                logger.error(f"Ошибка при добавлении задачи пользователем {request.user.username}: {e}", exc_info=True)
        else:
            logger.warning(f"Пользователь {request.user.username} попытался добавить задачу без текста или даты")
    offset = request.GET.get('offset', 0)
    return redirect(f'/?offset={offset}')


@login_required
def task_detail(request, task_id):
    """
    Детальная страница задачи (просмотр и редактирование).
    """
    try:
        task = get_object_or_404(Task, id=task_id, user=request.user)
        logger.debug(f"Пользователь {request.user.username} открыл задачу ID {task_id}")

        if request.method == 'POST':
            new_text = request.POST.get('text', task.text)
            new_description = request.POST.get('description', task.description)
            is_done = request.POST.get('is_done') == 'on'

            task.text = new_text
            task.description = new_description
            task.is_done = is_done
            task.save()

            logger.info(
                f"Пользователь {request.user.username} обновил задачу ID {task_id}: текст='{new_text}', выполнено={is_done}")
            return redirect('task_detail', task_id=task.id)

        return render(request, 'planner_app/task_detail.html', {'task': task})

    except Exception as e:
        logger.error(f"Ошибка в task_detail для пользователя {request.user.username}, задача ID {task_id}: {e}",
                     exc_info=True)
        # Можно перенаправить на главную или показать 404
        return redirect('week_view')


@login_required
def toggle_done(request, task_id):
    """
    Переключение статуса выполнения задачи.
    """
    try:
        task = get_object_or_404(Task, id=task_id, user=request.user)
        task.is_done = not task.is_done
        task.save()
        logger.info(f"Пользователь {request.user.username} переключил статус задачи ID {task_id} на {task.is_done}")
    except Exception as e:
        logger.error(f"Ошибка при переключении статуса задачи ID {task_id} пользователем {request.user.username}: {e}",
                     exc_info=True)

    offset = request.GET.get('offset', 0)
    return redirect(f'/?offset={offset}')


def signup(request):
    """
    Регистрация нового пользователя.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                logger.info(f"Зарегистрирован новый пользователь: {user.username}")
                # Можно автоматически залогинить:
                # login(request, user)
                return redirect('login')
            except Exception as e:
                logger.error(f"Ошибка при регистрации пользователя: {e}", exc_info=True)
        else:
            logger.warning(f"Неудачная попытка регистрации: ошибки формы {form.errors}")
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})