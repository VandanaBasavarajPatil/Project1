from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from . import views
from .auth import EmailTokenObtainPairView

# API URL patterns
urlpatterns = [
    # Authentication (compat + required endpoints)
    path('auth/register/', views.RegisterView.as_view(), name='register'),  # legacy path used by UI
    path('auth/login/', views.login_view, name='login'),                     # legacy path used by UI
    path('users/register/', views.RegisterView.as_view(), name='users-register'),
    path('token/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Dashboard endpoints
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
    
    # Project endpoints
    path('projects/', views.ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<uuid:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    
    # Task endpoints
    path('tasks/', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<uuid:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    
    # Time entry endpoints
    path('time-entries/', views.TimeEntryListCreateView.as_view(), name='timeentry-list-create'),
    path('time-entries/<uuid:pk>/', views.TimeEntryDetailView.as_view(), name='timeentry-detail'),
    
    # User endpoints
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<uuid:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/me/', views.me_view, name='user-profile'),
    
    # Comment endpoints
    path('tasks/<uuid:task_id>/comments/', views.CommentListCreateView.as_view(), name='comment-list-create'),
    
    # Notification endpoints
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/<uuid:pk>/read/', views.mark_notification_read, name='notification-read'),
    
    # Analytics endpoints
    path('analytics/productivity-trends/', views.analytics_productivity_trends, name='analytics-productivity'),
    path('analytics/team-performance/', views.analytics_team_performance, name='analytics-team'),
    path('analytics/task-distribution/', views.analytics_task_distribution, name='analytics-distribution'),
]