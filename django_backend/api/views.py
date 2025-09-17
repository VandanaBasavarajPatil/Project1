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
    """Get dashboard statistics"""
    user = request.user
    
    # Get task statistics
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(status='done').count()
    overdue_tasks = Task.objects.filter(
        due_date__lt=timezone.now(),
        status__in=['todo', 'in_progress', 'review']
    ).count()
    
    # Get active projects
    active_projects = Project.objects.filter(status='active').count()
    
    # Get recent tasks
    recent_tasks = Task.objects.select_related('assigned_to', 'created_by', 'project').order_by('-created_at')[:5]
    recent_tasks_data = TaskSerializer(recent_tasks, many=True).data
    
    # Calculate metrics using pandas for data processing
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Mock data for now - can be calculated from actual time entries
    avg_completion_time = 2.5
    team_productivity = 85.0
    daily_focus_time = 6.5
    
    # In real implementation, use pandas to process time entry data
    # time_entries_df = pd.DataFrame(list(TimeEntry.objects.values()))
    # if not time_entries_df.empty:
    #     avg_completion_time = time_entries_df['duration_hours'].mean()
    #     daily_focus_time = time_entries_df.groupby('user_id')['duration_hours'].sum().mean()
    
    stats = {
        'tasks_completed': completed_tasks,
        'avg_completion_time': avg_completion_time,
        'team_productivity': team_productivity,
        'overdue_tasks': overdue_tasks,
        'daily_focus_time': daily_focus_time,
        'completion_rate': completion_rate,
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
    queryset = Task.objects.select_related('assigned_to', 'created_by', 'project')
    serializer_class = TaskSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get('project_id')
        status_filter = self.request.query_params.get('status')
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a task"""
    queryset = Task.objects.select_related('assigned_to', 'created_by', 'project')
    serializer_class = TaskSerializer


# Time Entry Views
class TimeEntryListCreateView(generics.ListCreateAPIView):
    """List all time entries or create a new time entry"""
    queryset = TimeEntry.objects.select_related('user', 'task')
    serializer_class = TimeEntrySerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        task_id = self.request.query_params.get('task_id')
        user_id = self.request.query_params.get('user_id')
        
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TimeEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a time entry"""
    queryset = TimeEntry.objects.select_related('user', 'task')
    serializer_class = TimeEntrySerializer


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