from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Project, Task, TimeEntry, Comment, Notification


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model"""
    list_display = ['email', 'name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['email', 'name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'avatar')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin interface for Project model"""
    list_display = ['title', 'status', 'created_by', 'deadline', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description']
    filter_horizontal = ['team_members']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin interface for Task model"""
    list_display = ['title', 'status', 'priority', 'assigned_to', 'project', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'created_at', 'due_date']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('title', 'description')}),
        ('Assignment', {'fields': ('project', 'assigned_to', 'created_by')}),
        ('Details', {'fields': ('status', 'priority', 'due_date')}),
        ('Time Tracking', {'fields': ('estimated_hours', 'actual_hours')}),
    )


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    """Admin interface for TimeEntry model"""
    list_display = ['task', 'user', 'start_time', 'end_time', 'duration_hours']
    list_filter = ['start_time', 'user']
    search_fields = ['task__title', 'user__name']
    date_hierarchy = 'start_time'
    ordering = ['-start_time']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for Comment model"""
    list_display = ['task', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['task__title', 'user__name', 'content']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model"""
    list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'user__name']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']