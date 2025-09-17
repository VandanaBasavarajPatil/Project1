from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
import json
from datetime import datetime, timedelta
import pytz

from api.models import User, Project, Task, TaskTimer, ActivityLog


class TaskTimerTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
            name='Test User'
        )
        
        # Create test project
        self.project = Project.objects.create(
            title='Test Project',
            description='Test project description',
            created_by=self.user
        )
        
        # Create test task
        self.task = Task.objects.create(
            title='Test Task',
            description='Test task description',
            project=self.project,
            assigned_to=self.user,
            created_by=self.user
        )
        
        # Setup API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_start_timer_creates_entry_with_null_end_time(self):
        """Test that starting a timer creates an entry with null end_time"""
        url = reverse('task-timer-start', kwargs={'task_id': self.task.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that a timer was created
        timer = TaskTimer.objects.filter(task=self.task, user=self.user).first()
        self.assertIsNotNone(timer)
        self.assertIsNotNone(timer.start_time)
        self.assertIsNone(timer.end_time)
        self.assertIsNone(timer.duration_seconds)
        
        # Check that an activity log was created
        log = ActivityLog.objects.filter(
            task=self.task,
            user=self.user,
            action='created'
        ).first()
        self.assertIsNotNone(log)
    
    def test_stop_timer_fills_end_time_and_duration(self):
        """Test that stopping a timer fills end_time and calculates duration"""
        # Create a timer
        start_time = timezone.now() - timedelta(minutes=5)
        timer = TaskTimer.objects.create(
            task=self.task,
            user=self.user,
            start_time=start_time
        )
        
        url = reverse('task-timer-stop', kwargs={'task_id': self.task.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh timer from database
        timer.refresh_from_db()
        
        # Check that end_time is set and duration is calculated
        self.assertIsNotNone(timer.end_time)
        self.assertIsNotNone(timer.duration_seconds)
        self.assertTrue(timer.duration_seconds > 0)
        
        # Check that duration is approximately 5 minutes (300 seconds)
        self.assertGreaterEqual(timer.duration_seconds, 290)
        self.assertLessEqual(timer.duration_seconds, 310)
        
        # Check that an activity log was created
        log = ActivityLog.objects.filter(
            task=self.task,
            user=self.user,
            action='updated'
        ).first()
        self.assertIsNotNone(log)
    
    def test_daily_timesheet_aggregation(self):
        """Test that daily timesheet aggregation returns correct sums"""
        # Create multiple timers for today
        today = timezone.now().date()
        start_time1 = datetime.combine(today, datetime.min.time().replace(hour=9))
        start_time1 = pytz.timezone('UTC').localize(start_time1)
        
        # Timer 1: 1 hour
        timer1 = TaskTimer.objects.create(
            task=self.task,
            user=self.user,
            start_time=start_time1,
            end_time=start_time1 + timedelta(hours=1),
            duration_seconds=3600
        )
        
        # Timer 2: 30 minutes
        timer2 = TaskTimer.objects.create(
            task=self.task,
            user=self.user,
            start_time=start_time1 + timedelta(hours=2),
            end_time=start_time1 + timedelta(hours=2, minutes=30),
            duration_seconds=1800
        )
        
        # Create another task and timer
        task2 = Task.objects.create(
            title='Another Task',
            description='Another task description',
            project=self.project,
            assigned_to=self.user,
            created_by=self.user
        )
        
        # Timer 3: 45 minutes on different task
        timer3 = TaskTimer.objects.create(
            task=task2,
            user=self.user,
            start_time=start_time1 + timedelta(hours=4),
            end_time=start_time1 + timedelta(hours=4, minutes=45),
            duration_seconds=2700
        )
        
        url = reverse('timesheet-daily')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check the response data
        data = response.data
        self.assertEqual(data['total_duration_seconds'], 8100)  # 3600 + 1800 + 2700 = 8100
        
        # Check that entries are correctly aggregated by task
        entries = data['entries']
        self.assertEqual(len(entries), 2)  # Should have 2 entries (one per task)
        
        # Find entries for each task
        task1_entry = next((e for e in entries if e['task_id'] == str(self.task.id)), None)
        task2_entry = next((e for e in entries if e['task_id'] == str(task2.id)), None)
        
        self.assertIsNotNone(task1_entry)
        self.assertIsNotNone(task2_entry)
        
        # Check durations
        self.assertEqual(task1_entry['total_duration_seconds'], 5400)  # 3600 + 1800 = 5400
        self.assertEqual(task2_entry['total_duration_seconds'], 2700)
    
    def test_weekly_timesheet_aggregation(self):
        """Test that weekly timesheet aggregation returns correct sums"""
        # Create a date in the middle of the week
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        # Create timers for different days in the week
        for day_offset in range(3):  # Create timers for 3 days
            day = week_start + timedelta(days=day_offset)
            start_time = datetime.combine(day, datetime.min.time().replace(hour=9))
            start_time = pytz.timezone('UTC').localize(start_time)
            
            # Create a timer with 2 hours duration
            TaskTimer.objects.create(
                task=self.task,
                user=self.user,
                start_time=start_time,
                end_time=start_time + timedelta(hours=2),
                duration_seconds=7200
            )
        
        url = reverse('timesheet-weekly')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check the response data
        data = response.data
        self.assertEqual(data['total_duration_seconds'], 21600)  # 3 days * 7200 seconds = 21600
        
        # Check that entries are correctly aggregated
        entries = data['entries']
        self.assertEqual(len(entries), 1)  # Should have 1 entry (one task)
        
        # Check the entry
        entry = entries[0]
        self.assertEqual(entry['task_id'], str(self.task.id))
        self.assertEqual(entry['total_duration_seconds'], 21600)