from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from .models import Task, Notification, User


def create_notification(user, title, message, notification_type='task_due'):
    """Create a notification for a user"""
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type
    )
    return notification


def check_due_tasks():
    """Check for tasks that are due soon and create notifications"""
    now = timezone.now()
    tomorrow = now + timedelta(days=1)
    
    # Find tasks due within 24 hours
    upcoming_tasks = Task.objects.filter(
        due_date__lte=tomorrow,
        due_date__gt=now,
        status__in=['todo', 'in_progress', 'review']
    ).select_related('assigned_to', 'project')
    
    for task in upcoming_tasks:
        if task.assigned_to:
            # Check if notification already exists for this task
            existing_notification = Notification.objects.filter(
                user=task.assigned_to,
                title__icontains=task.title,
                notification_type='task_due',
                created_at__gte=now - timedelta(hours=12)
            ).exists()
            
            if not existing_notification:
                create_notification(
                    user=task.assigned_to,
                    title=f'Task Due Soon: {task.title}',
                    message=f'Your task "{task.title}" is due on {task.due_date.strftime("%B %d, %Y at %I:%M %p")}',
                    notification_type='task_due'
                )


def check_overdue_tasks():
    """Check for overdue tasks and create notifications"""
    now = timezone.now()
    
    # Find overdue tasks
    overdue_tasks = Task.objects.filter(
        due_date__lt=now,
        status__in=['todo', 'in_progress', 'review']
    ).select_related('assigned_to', 'project')
    
    for task in overdue_tasks:
        if task.assigned_to:
            # Check if notification already exists for this task today
            existing_notification = Notification.objects.filter(
                user=task.assigned_to,
                title__icontains=task.title,
                notification_type='task_due',
                created_at__gte=now.replace(hour=0, minute=0, second=0, microsecond=0)
            ).exists()
            
            if not existing_notification:
                days_overdue = (now.date() - task.due_date.date()).days
                create_notification(
                    user=task.assigned_to,
                    title=f'Overdue Task: {task.title}',
                    message=f'Your task "{task.title}" was due {days_overdue} day(s) ago',
                    notification_type='task_due'
                )


def notify_task_assignment(task):
    """Create notification when a task is assigned to a user"""
    if task.assigned_to:
        create_notification(
            user=task.assigned_to,
            title=f'New Task Assigned: {task.title}',
            message=f'You have been assigned a new task: "{task.title}"',
            notification_type='task_assigned'
        )


def notify_task_comment(comment):
    """Create notification when a comment is added to a task"""
    task = comment.task
    
    # Notify assigned user if different from commenter
    if task.assigned_to and task.assigned_to != comment.user:
        create_notification(
            user=task.assigned_to,
            title=f'New Comment on Task: {task.title}',
            message=f'{comment.user.name} commented: "{comment.content[:100]}..."',
            notification_type='comment_added'
        )
    
    # Notify task creator if different from commenter and assigned user
    if (task.created_by and 
        task.created_by != comment.user and 
        task.created_by != task.assigned_to):
        create_notification(
            user=task.created_by,
            title=f'New Comment on Task: {task.title}',
            message=f'{comment.user.name} commented: "{comment.content[:100]}..."',
            notification_type='comment_added'
        )


def notify_project_update(project, message):
    """Create notification for all project team members"""
    for member in project.team_members.all():
        create_notification(
            user=member,
            title=f'Project Update: {project.title}',
            message=message,
            notification_type='project_update'
        )


def get_user_notification_summary(user):
    """Get notification summary for a user"""
    unread_count = Notification.objects.filter(user=user, is_read=False).count()
    
    recent_notifications = Notification.objects.filter(
        user=user
    ).order_by('-created_at')[:5]
    
    return {
        'unread_count': unread_count,
        'recent_notifications': recent_notifications
    }