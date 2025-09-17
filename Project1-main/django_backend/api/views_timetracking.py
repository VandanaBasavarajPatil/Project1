from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Sum, F
from datetime import datetime, timedelta
import pytz

from .models import Task, TaskTimer, ActivityLog
from .serializers_timetracking import TaskTimerSerializer, TimesheetSummarySerializer, TimesheetEntrySerializer

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_timer(request, task_id):
    """Start a timer for a task"""
    task = get_object_or_404(Task, pk=task_id)
    
    # Check if user already has an active timer for this task
    active_timer = TaskTimer.objects.filter(
        task=task,
        user=request.user,
        end_time__isnull=True
    ).first()
    
    if active_timer:
        return Response(
            {"detail": "You already have an active timer for this task"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create new timer
    timer = TaskTimer.objects.create(
        task=task,
        user=request.user,
        start_time=timezone.now()
    )
    
    # Log activity
    ActivityLog.objects.create(
        user=request.user,
        task=task,
        action='created',
        description=f"Started timer for task: {task.title}"
    )
    
    serializer = TaskTimerSerializer(timer)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def stop_timer(request, task_id):
    """Stop an active timer for a task"""
    task = get_object_or_404(Task, pk=task_id)
    
    # Find active timer
    timer = TaskTimer.objects.filter(
        task=task,
        user=request.user,
        end_time__isnull=True
    ).first()
    
    if not timer:
        return Response(
            {"detail": "No active timer found for this task"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Stop timer
    timer.end_time = timezone.now()
    timer.save()  # This will trigger the save method to calculate duration
    
    # Log activity
    ActivityLog.objects.create(
        user=request.user,
        task=task,
        action='updated',
        description=f"Stopped timer for task: {task.title}. Duration: {timer.duration_seconds} seconds"
    )
    
    serializer = TaskTimerSerializer(timer)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def daily_timesheet(request):
    """Get daily timesheet summary"""
    date_str = request.query_params.get('date', None)
    
    try:
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date = timezone.now().date()
            
        # Get start and end of day
        start_datetime = datetime.combine(date, datetime.min.time())
        end_datetime = datetime.combine(date, datetime.max.time())
        
        # Make timezone-aware
        start_datetime = timezone.make_aware(start_datetime)
        end_datetime = timezone.make_aware(end_datetime)
        
        # Query timers for the day
        timers = TaskTimer.objects.filter(
            user=request.user,
            start_time__gte=start_datetime,
            start_time__lte=end_datetime,
            end_time__isnull=False  # Only completed timers
        )
        
        # Aggregate by task
        entries = []
        total_duration = 0
        
        # Group by task and project
        task_durations = {}
        
        for timer in timers:
            task_id = str(timer.task.id)
            if task_id not in task_durations:
                task_durations[task_id] = {
                    'task_id': task_id,
                    'task_title': timer.task.title,
                    'project_id': str(timer.task.project.id) if timer.task.project else None,
                    'project_title': timer.task.project.title if timer.task.project else 'No Project',
                    'total_duration_seconds': 0
                }
            
            task_durations[task_id]['total_duration_seconds'] += timer.duration_seconds or 0
            total_duration += timer.duration_seconds or 0
        
        entries = list(task_durations.values())
        
        # Prepare response
        data = {
            'date': date,
            'total_duration_seconds': total_duration,
            'entries': entries
        }
        
        serializer = TimesheetSummarySerializer(data)
        return Response(serializer.data)
        
    except ValueError:
        return Response(
            {"detail": "Invalid date format. Use YYYY-MM-DD"},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def weekly_timesheet(request):
    """Get weekly timesheet summary"""
    week_start_str = request.query_params.get('week_start', None)
    
    try:
        if week_start_str:
            week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date()
        else:
            # Default to current week (starting Monday)
            today = timezone.now().date()
            week_start = today - timedelta(days=today.weekday())
            
        # Calculate week end (Sunday)
        week_end = week_start + timedelta(days=6)
        
        # Get start and end datetime
        start_datetime = datetime.combine(week_start, datetime.min.time())
        end_datetime = datetime.combine(week_end, datetime.max.time())
        
        # Make timezone-aware
        start_datetime = timezone.make_aware(start_datetime)
        end_datetime = timezone.make_aware(end_datetime)
        
        # Query timers for the week
        timers = TaskTimer.objects.filter(
            user=request.user,
            start_time__gte=start_datetime,
            start_time__lte=end_datetime,
            end_time__isnull=False  # Only completed timers
        )
        
        # Aggregate by task
        entries = []
        total_duration = 0
        
        # Group by task and project
        task_durations = {}
        
        for timer in timers:
            task_id = str(timer.task.id)
            if task_id not in task_durations:
                task_durations[task_id] = {
                    'task_id': task_id,
                    'task_title': timer.task.title,
                    'project_id': str(timer.task.project.id) if timer.task.project else None,
                    'project_title': timer.task.project.title if timer.task.project else 'No Project',
                    'total_duration_seconds': 0
                }
            
            task_durations[task_id]['total_duration_seconds'] += timer.duration_seconds or 0
            total_duration += timer.duration_seconds or 0
        
        entries = list(task_durations.values())
        
        # Prepare response
        data = {
            'week_start': week_start,
            'week_end': week_end,
            'total_duration_seconds': total_duration,
            'entries': entries
        }
        
        serializer = TimesheetSummarySerializer(data)
        return Response(serializer.data)
        
    except ValueError:
        return Response(
            {"detail": "Invalid date format. Use YYYY-MM-DD"},
            status=status.HTTP_400_BAD_REQUEST
        )