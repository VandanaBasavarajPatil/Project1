from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from . import views
from .auth import EmailTokenObtainPairView
from . import views_timetracking

# API URL patterns
urlpatterns = [
    # Authentication (compat + required endpoints)
    path('auth/register/', views.RegisterView.as_view(), name='register'),  # legacy path used by UI
    path('auth/login/', views.login_view, name='login'),                     # legacy path used by UI
    path('auth/me/', views.me_view, name='auth-me'),                         # new endpoint for auth
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
    path('time-entries/start-timer/', views.start_timer, name='start-timer'),
    path('time-entries/stop-timer/', views.stop_timer, name='stop-timer'),
    path('time-entries/active-timer/', views.active_timer, name='active-timer'),
    path('time-entries/summary/', views.time_summary, name='time-summary'),
    
    # User endpoints
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<uuid:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/me/', views.me_view, name='user-profile'),
    path('users/change-password/', views.change_password, name='change-password'),
    path('users/update-profile/', views.update_profile, name='update-profile'),
    path('users/preferences/', views.user_preferences, name='user-preferences'),
    
    # Comment endpoints
    path('tasks/<uuid:task_id>/comments/', views.CommentListCreateView.as_view(), name='comment-list-create'),
    
    # Notification endpoints
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    
    # Time tracking endpoints
    path('tasks/<uuid:task_id>/timer/start/', views_timetracking.start_timer, name='task-timer-start'),
    path('tasks/<uuid:task_id>/timer/stop/', views_timetracking.stop_timer, name='task-timer-stop'),
    path('timesheets/daily/', views_timetracking.daily_timesheet, name='timesheet-daily'),
    path('timesheets/weekly/', views_timetracking.weekly_timesheet, name='timesheet-weekly'),
    path('notifications/<uuid:pk>/read/', views.mark_notification_read, name='notification-read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='notification-mark-all-read'),
    path('notifications/summary/', views.notification_summary, name='notification-summary'),
    path('notifications/check-reminders/', views.check_reminders, name='check-reminders'),
    
    # Analytics endpoints
    path('analytics/productivity-trends/', views.analytics_productivity_trends, name='analytics-productivity'),
    path('analytics/team-performance/', views.analytics_team_performance, name='analytics-team'),
    path('analytics/task-distribution/', views.analytics_task_distribution, name='analytics-distribution'),
    
    # Attachment endpoints
    path('tasks/<uuid:task_id>/attachments/', views.AttachmentListCreateView.as_view(), name='attachment-list-create'),
    path('attachments/<uuid:pk>/', views.AttachmentDetailView.as_view(), name='attachment-detail'),
    path('attachments/', views.AttachmentListCreateView.as_view(), name='attachments-list'),
    
    # Activity log endpoints
    path('activity-logs/', views.ActivityLogListView.as_view(), name='activity-log-list'),
    path('activity-logs/recent/', views.recent_activity, name='recent-activity'),
]