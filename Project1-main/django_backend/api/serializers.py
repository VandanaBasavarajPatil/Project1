from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, Project, Task, TimeEntry, Comment, Notification, Attachment, ActivityLog


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'avatar', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'role']
    
    def validate(self, attrs):
        # Check if user is trying to create a SCRUM_MASTER
        request = self.context.get('request')
        if attrs.get('role') == 'SCRUM_MASTER' and request and request.user.is_authenticated:
            # Only existing SCRUM_MASTER or admin can create another SCRUM_MASTER
            if not (request.user.role == 'SCRUM_MASTER' or request.user.is_staff):
                raise serializers.ValidationError(
                    {"role": "Only Scrum Masters or admins can create another Scrum Master"}
                )
        return attrs
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        
        # Default to EMPLOYEE if role is not provided
        if 'role' not in validated_data:
            validated_data['role'] = 'EMPLOYEE'
            
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            **validated_data
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'),
                              username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
        else:
            raise serializers.ValidationError('Must include email and password')
        
        attrs['user'] = user
        return attrs


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model"""
    created_by = UserSerializer(read_only=True)
    team_members = UserSerializer(many=True, read_only=True)
    team_member_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True, required=False
    )
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_by', 
                 'team_members', 'team_member_ids', 'task_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_task_count(self, obj):
        return obj.tasks.count()
    
    def create(self, validated_data):
        team_member_ids = validated_data.pop('team_member_ids', [])
        project = Project.objects.create(**validated_data)
        if team_member_ids:
            project.team_members.set(team_member_ids)
        return project
    
    def update(self, instance, validated_data):
        team_member_ids = validated_data.pop('team_member_ids', None)
        instance = super().update(instance, validated_data)
        if team_member_ids is not None:
            instance.team_members.set(team_member_ids)
        return instance


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model"""
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=False, allow_null=True
    )
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), write_only=True, required=False, allow_null=True
    )
    time_spent = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'project', 'project_id',
                 'assigned_to', 'assigned_to_id', 'created_by', 'due_date', 'estimated_hours',
                 'actual_hours', 'time_spent', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_time_spent(self, obj):
        return sum(entry.duration_hours or 0 for entry in obj.time_entries.all())
    
    def create(self, validated_data):
        assigned_to_id = validated_data.pop('assigned_to_id', None)
        project_id = validated_data.pop('project_id', None)
        
        task = Task.objects.create(**validated_data)
        
        if assigned_to_id:
            task.assigned_to = assigned_to_id
        if project_id:
            task.project = project_id
        
        task.save()
        return task
    
    def update(self, instance, validated_data):
        assigned_to_id = validated_data.pop('assigned_to_id', None)
        project_id = validated_data.pop('project_id', None)
        
        instance = super().update(instance, validated_data)
        
        if assigned_to_id is not None:
            instance.assigned_to = assigned_to_id
        if project_id is not None:
            instance.project = project_id
        
        instance.save()
        return instance


class TimeEntrySerializer(serializers.ModelSerializer):
    """Serializer for TimeEntry model"""
    user = UserSerializer(read_only=True)
    task = TaskSerializer(read_only=True)
    task_id = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), write_only=True)
    
    class Meta:
        model = TimeEntry
        fields = ['id', 'task', 'task_id', 'user', 'start_time', 'end_time', 
                 'duration_hours', 'description', 'created_at']
        read_only_fields = ['id', 'user', 'duration_hours', 'created_at']
    
    def create(self, validated_data):
        task_id = validated_data.pop('task_id')
        time_entry = TimeEntry.objects.create(task=task_id, **validated_data)
        return time_entry


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""
    user = UserSerializer(read_only=True)
    task = TaskSerializer(read_only=True)
    task_id = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), write_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'task', 'task_id', 'user', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        task_id = validated_data.pop('task_id')
        comment = Comment.objects.create(task=task_id, **validated_data)
        return comment


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']


class AttachmentSerializer(serializers.ModelSerializer):
    """Serializer for Attachment model"""
    uploaded_by = UserSerializer(read_only=True)
    task_id = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), write_only=True)
    
    class Meta:
        model = Attachment
        fields = ['id', 'task_id', 'uploaded_by', 'file_name', 'file_size', 
                 'file_type', 'file_url', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at']
    
    def create(self, validated_data):
        task_id = validated_data.pop('task_id')
        attachment = Attachment.objects.create(task=task_id, **validated_data)
        return attachment


class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for ActivityLog model"""
    user = UserSerializer(read_only=True)
    task = TaskSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'task', 'project', 'action', 'description', 
                 'metadata', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    tasks_completed = serializers.IntegerField()
    avg_completion_time = serializers.FloatField()
    team_productivity = serializers.FloatField()
    overdue_tasks = serializers.IntegerField()
    daily_focus_time = serializers.FloatField()
    completion_rate = serializers.FloatField()
    active_projects = serializers.IntegerField()
    recent_tasks = TaskSerializer(many=True)