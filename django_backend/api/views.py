from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta
import pandas as pd

from .models import User, Project, Task, TimeEntry, Comment, Notification
from .serializers import (
    UserSerializer, UserCreateSerializer, UserLoginSerializer,
    ProjectSerializer, TaskSerializer, TimeEntrySerializer,
    CommentSerializer, NotificationSerializer, DashboardStatsSerializer
)
from .permissions import (
    IsScrumMasterOrReadOnly, IsScrumMaster, IsOwnerOrScrumMaster,
    IsAssignedOrScrumMaster, CanAccessProject, CanAccessTask
)


# Authentication Views
class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        user_data = UserSerializer(user).data
        
        return Response({
            'access_token': access_token,  # keep for existing frontend usage
            'access': access_token,        # standard SimpleJWT key
            'refresh': str(refresh),
            'token_type': 'bearer',
            'user': user_data
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """User login endpoint"""
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = serializer.validated_data['user']
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    user_data = UserSerializer(user).data
    
    return Response({
        'access_token': access_token,
        'token_type': 'bearer',
        'user': user_data
    })


# Dashboard Views
@api_view(['GET'])
def dashboard_stats(request):
    """Get dashboard statistics with role-based filtering"""
    user = request.user
    
    # Apply role-based filtering
    if user.role == 'scrum_master':
        tasks_queryset = Task.objects.all()
        projects_queryset = Project.objects.all()
    else:
        tasks_queryset = Task.objects.filter(
            Q(assigned_to=user) |
            Q(created_by=user) |
            Q(project__team_members=user)
        ).distinct()
        projects_queryset = Project.objects.filter(team_members=user)
    
    # Get task statistics
    total_tasks = tasks_queryset.count()
    completed_tasks = tasks_queryset.filter(status='done').count()
    overdue_tasks = tasks_queryset.filter(
        due_date__lt=timezone.now(),
        status__in=['todo', 'in_progress', 'review']
    ).count()
    
    # Get active projects
    active_projects = projects_queryset.filter(status='active').count()
    
    # Get recent tasks
    recent_tasks = tasks_queryset.select_related('assigned_to', 'created_by', 'project').order_by('-created_at')[:5]
    recent_tasks_data = TaskSerializer(recent_tasks, many=True).data
    
    # Calculate real metrics using pandas for data processing
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Calculate real time-based metrics
    time_entries = TimeEntry.objects.filter(
        user=user,
        end_time__isnull=False,
        start_time__gte=timezone.now() - timedelta(days=30)
    )
    
    if time_entries.exists():
        # Use pandas for analysis
        time_data = list(time_entries.values('duration_hours', 'start_time', 'task_id'))
        df = pd.DataFrame(time_data)
        
        if not df.empty:
            avg_completion_time = df['duration_hours'].mean()
            daily_focus_time = df.groupby(df['start_time'].dt.date)['duration_hours'].sum().mean()
        else:
            avg_completion_time = 0
            daily_focus_time = 0
    else:
        avg_completion_time = 0
        daily_focus_time = 0
    
    # Calculate team productivity (completion rate * efficiency)
    team_productivity = completion_rate * 0.85 if completion_rate > 0 else 0
    
    stats = {
        'tasks_completed': completed_tasks,
        'avg_completion_time': round(avg_completion_time, 1),
        'team_productivity': round(team_productivity, 1),
        'overdue_tasks': overdue_tasks,
        'daily_focus_time': round(daily_focus_time, 1),
        'completion_rate': round(completion_rate, 1),
        'active_projects': active_projects,
        'recent_tasks': recent_tasks_data
    }
    
    return Response(stats)


# Project Views
class ProjectListCreateView(generics.ListCreateAPIView):
    """List all projects or create a new project"""
    serializer_class = ProjectSerializer
    permission_classes = [IsScrumMasterOrReadOnly]
    
    def get_queryset(self):
        """Filter projects based on user role"""
        user = self.request.user
        if user.role == 'scrum_master':
            return Project.objects.all()
        else:
            # Employees can only see projects they're team members of
            return Project.objects.filter(team_members=user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a project"""
    serializer_class = ProjectSerializer
    permission_classes = [CanAccessProject, IsScrumMasterOrReadOnly]
    
    def get_queryset(self):
        """Filter projects based on user role"""
        user = self.request.user
        if user.role == 'scrum_master':
            return Project.objects.all()
        else:
            return Project.objects.filter(team_members=user)


# Task Views
class TaskListCreateView(generics.ListCreateAPIView):
    """List all tasks or create a new task"""
    serializer_class = TaskSerializer
    permission_classes = [IsScrumMasterOrReadOnly]
    
    def get_queryset(self):
        """Filter tasks based on user role and permissions"""
        user = self.request.user
        queryset = Task.objects.select_related('assigned_to', 'created_by', 'project')
        
        # Filter by project_id and status if provided
        project_id = self.request.query_params.get('project_id')
        status_filter = self.request.query_params.get('status')
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Apply role-based filtering
        if user.role == 'scrum_master':
            return queryset
        else:
            # Employees can only see tasks assigned to them or in projects they're part of
            return queryset.filter(
                Q(assigned_to=user) |
                Q(created_by=user) |
                Q(project__team_members=user)
            ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a task"""
    serializer_class = TaskSerializer
    permission_classes = [CanAccessTask, IsAssignedOrScrumMaster]
    
    def get_queryset(self):
        """Filter tasks based on user role"""
        user = self.request.user
        queryset = Task.objects.select_related('assigned_to', 'created_by', 'project')
        
        if user.role == 'scrum_master':
            return queryset
        else:
            return queryset.filter(
                Q(assigned_to=user) |
                Q(created_by=user) |
                Q(project__team_members=user)
            ).distinct()


# Time Entry Views
class TimeEntryListCreateView(generics.ListCreateAPIView):
    """List all time entries or create a new time entry"""
    serializer_class = TimeEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter time entries based on user role"""
        user = self.request.user
        queryset = TimeEntry.objects.select_related('user', 'task')
        
        task_id = self.request.query_params.get('task_id')
        user_id = self.request.query_params.get('user_id')
        
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Role-based filtering
        if user.role == 'scrum_master':
            return queryset
        else:
            # Employees can only see their own time entries
            return queryset.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TimeEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a time entry"""
    serializer_class = TimeEntrySerializer
    permission_classes = [IsOwnerOrScrumMaster]
    
    def get_queryset(self):
        """Filter time entries based on user role"""
        user = self.request.user
        queryset = TimeEntry.objects.select_related('user', 'task')
        
        if user.role == 'scrum_master':
            return queryset
        else:
            return queryset.filter(user=user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_timer(request):
    """Start a timer for a task"""
    task_id = request.data.get('task_id')
    description = request.data.get('description', '')
    
    if not task_id:
        return Response({'error': 'task_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        task = Task.objects.get(id=task_id)
        
        # Check if user can access this task
        user = request.user
        if user.role != 'scrum_master':
            if not (task.assigned_to == user or task.created_by == user or 
                   (task.project and task.project.team_members.filter(id=user.id).exists())):
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if user already has an active timer
        active_timer = TimeEntry.objects.filter(
            user=user,
            end_time__isnull=True
        ).first()
        
        if active_timer:
            return Response({
                'error': 'You already have an active timer',
                'active_timer': TimeEntrySerializer(active_timer).data
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create new time entry
        time_entry = TimeEntry.objects.create(
            task=task,
            user=user,
            start_time=timezone.now(),
            description=description
        )
        
        return Response(TimeEntrySerializer(time_entry).data, status=status.HTTP_201_CREATED)
        
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def stop_timer(request):
    """Stop the active timer"""
    time_entry_id = request.data.get('time_entry_id')
    user = request.user
    
    if time_entry_id:
        try:
            time_entry = TimeEntry.objects.get(id=time_entry_id, user=user, end_time__isnull=True)
        except TimeEntry.DoesNotExist:
            return Response({'error': 'Active timer not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        # Find user's active timer
        time_entry = TimeEntry.objects.filter(
            user=user,
            end_time__isnull=True
        ).first()
        
        if not time_entry:
            return Response({'error': 'No active timer found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Stop the timer
    time_entry.end_time = timezone.now()
    time_entry.save()  # This will trigger the duration calculation in the model
    
    # Update task actual hours
    task = time_entry.task
    task.actual_hours += time_entry.duration_hours or 0
    task.save()
    
    return Response(TimeEntrySerializer(time_entry).data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def active_timer(request):
    """Get user's active timer"""
    user = request.user
    active_timer = TimeEntry.objects.filter(
        user=user,
        end_time__isnull=True
    ).first()
    
    if active_timer:
        return Response(TimeEntrySerializer(active_timer).data)
    else:
        return Response({'active_timer': None})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def time_summary(request):
    """Get time tracking summary for the user"""
    user = request.user
    
    # Get date range from query params
    days = int(request.GET.get('days', 7))  # Default to last 7 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Get time entries for the period
    time_entries = TimeEntry.objects.filter(
        user=user,
        start_time__date__gte=start_date,
        start_time__date__lte=end_date,
        end_time__isnull=False
    ).select_related('task', 'task__project')
    
    # Calculate summary statistics
    total_hours = sum(entry.duration_hours or 0 for entry in time_entries)
    total_entries = len(time_entries)
    
    # Group by date
    daily_summary = {}
    for entry in time_entries:
        date_str = entry.start_time.date().isoformat()
        if date_str not in daily_summary:
            daily_summary[date_str] = {
                'date': date_str,
                'total_hours': 0,
                'entries': []
            }
        daily_summary[date_str]['total_hours'] += entry.duration_hours or 0
        daily_summary[date_str]['entries'].append(TimeEntrySerializer(entry).data)
    
    # Group by project
    project_summary = {}
    for entry in time_entries:
        project_name = entry.task.project.title if entry.task.project else 'No Project'
        if project_name not in project_summary:
            project_summary[project_name] = {
                'project': project_name,
                'total_hours': 0,
                'task_count': set()
            }
        project_summary[project_name]['total_hours'] += entry.duration_hours or 0
        project_summary[project_name]['task_count'].add(entry.task.id)
    
    # Convert sets to counts
    for proj in project_summary.values():
        proj['task_count'] = len(proj['task_count'])
    
    return Response({
        'period': f'Last {days} days',
        'total_hours': round(total_hours, 2),
        'total_entries': total_entries,
        'average_hours_per_day': round(total_hours / days, 2) if days > 0 else 0,
        'daily_summary': list(daily_summary.values()),
        'project_summary': list(project_summary.values())
    })


# User Views
class UserListView(generics.ListAPIView):
    """List all users"""
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer


class UserDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update user details"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_object(self):
        if self.kwargs.get('pk') == 'me':
            return self.request.user
        return super().get_object()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def me_view(request):
    """Return the current authenticated user's profile"""
    return Response(UserSerializer(request.user).data)


# Comment Views
class CommentListCreateView(generics.ListCreateAPIView):
    """List comments or create a new comment"""
    queryset = Comment.objects.select_related('user', 'task')
    serializer_class = CommentSerializer
    
    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        if task_id:
            return self.queryset.filter(task_id=task_id)
        return self.queryset
    
    def perform_create(self, serializer):
        task_id = self.kwargs.get('task_id')
        serializer.save(user=self.request.user, task_id=task_id)


# Notification Views
class NotificationListView(generics.ListAPIView):
    """List user notifications"""
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


@api_view(['PATCH'])
def mark_notification_read(request, pk):
    """Mark a notification as read"""
    try:
        notification = Notification.objects.get(pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)


# Analytics Views
@api_view(['GET'])
def analytics_productivity_trends(request):
    """Get productivity trends for analytics"""
    # Use pandas for data analysis
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Get task completion data
    tasks = Task.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    ).values('created_at', 'status', 'priority')
    
    # Convert to DataFrame for analysis
    if tasks:
        df = pd.DataFrame(list(tasks))
        df['date'] = pd.to_datetime(df['created_at']).dt.date
        
        # Group by date and calculate completion rates
        daily_stats = df.groupby('date').agg({
            'status': lambda x: (x == 'done').sum(),  # completed tasks
            'priority': 'count'  # total tasks
        }).reset_index()
        
        daily_stats['completion_rate'] = (daily_stats['status'] / daily_stats['priority'] * 100).round(2)
        daily_stats = daily_stats.rename(columns={'status': 'completed', 'priority': 'total'})
        
        trends = daily_stats.to_dict('records')
    else:
        trends = []
    
    return Response({
        'trends': trends,
        'period': '30_days'
    })


@api_view(['GET'])
def analytics_team_performance(request):
    """Get team performance analytics"""
    users = User.objects.filter(is_active=True)
    performance_data = []
    
    for user in users:
        user_tasks = Task.objects.filter(assigned_to=user)
        completed_tasks = user_tasks.filter(status='done').count()
        total_tasks = user_tasks.count()
        
        # Calculate time entries for this user
        time_entries = TimeEntry.objects.filter(user=user)
        total_hours = sum(entry.duration_hours or 0 for entry in time_entries)
        
        performance_data.append({
            'user_id': str(user.id),
            'user_name': user.name,
            'completed_tasks': completed_tasks,
            'total_tasks': total_tasks,
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'total_hours': total_hours,
            'avg_hours_per_task': (total_hours / completed_tasks) if completed_tasks > 0 else 0
        })
    
    return Response({
        'team_performance': performance_data
    })


@api_view(['GET'])
def analytics_task_distribution(request):
    """Get task distribution by status and priority"""
    # Status distribution
    status_distribution = list(Task.objects.values('status').annotate(count=Count('id')))
    
    # Priority distribution
    priority_distribution = list(Task.objects.values('priority').annotate(count=Count('id')))
    
    # Project distribution
    project_distribution = list(
        Task.objects.select_related('project')
        .values('project__title')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    
    return Response({
        'status_distribution': status_distribution,
        'priority_distribution': priority_distribution,
        'project_distribution': project_distribution
    })