from rest_framework import serializers
from .models import TaskTimer, Task, User
from django.db.models import Sum
from django.utils import timezone
import datetime

class TaskTimerSerializer(serializers.ModelSerializer):
    """Serializer for TaskTimer model"""
    task_title = serializers.CharField(source='task.title', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = TaskTimer
        fields = ['id', 'task', 'task_title', 'user', 'user_name', 'start_time', 
                 'end_time', 'duration_seconds', 'created_at', 'updated_at']
        read_only_fields = ['id', 'duration_seconds', 'created_at', 'updated_at']

class TimesheetEntrySerializer(serializers.Serializer):
    """Serializer for timesheet entries (aggregated data)"""
    task_id = serializers.UUIDField()
    task_title = serializers.CharField()
    project_id = serializers.UUIDField()
    project_title = serializers.CharField()
    total_duration_seconds = serializers.IntegerField()
    total_duration_formatted = serializers.SerializerMethodField()
    
    def get_total_duration_formatted(self, obj):
        """Format duration in hours and minutes"""
        total_seconds = obj.get('total_duration_seconds', 0)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m"

class TimesheetSummarySerializer(serializers.Serializer):
    """Serializer for timesheet summary"""
    date = serializers.DateField(required=False)
    week_start = serializers.DateField(required=False)
    week_end = serializers.DateField(required=False)
    total_duration_seconds = serializers.IntegerField()
    total_duration_formatted = serializers.SerializerMethodField()
    entries = TimesheetEntrySerializer(many=True)
    
    def get_total_duration_formatted(self, obj):
        """Format duration in hours and minutes"""
        total_seconds = obj.get('total_duration_seconds', 0)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m"