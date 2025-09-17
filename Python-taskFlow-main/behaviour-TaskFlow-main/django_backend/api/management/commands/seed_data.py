from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
from api.models import User, Project, Task, TimeEntry


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create additional users
        users_data = [
            {'email': 'alice@taskflow.com', 'name': 'Alice Johnson', 'role': 'scrum_master'},
            {'email': 'bob@taskflow.com', 'name': 'Bob Smith', 'role': 'employee'},
            {'email': 'carol@taskflow.com', 'name': 'Carol Davis', 'role': 'employee'},
            {'email': 'david@taskflow.com', 'name': 'David Wilson', 'role': 'employee'},
        ]

        users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'username': user_data['email'],
                    'name': user_data['name'],
                    'role': user_data['role'],
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created user: {user.name}')
            users.append(user)

        # Create projects
        projects_data = [
            {
                'title': 'TaskFlow Mobile App',
                'description': 'Develop mobile version of TaskFlow',
                'status': 'active',
                'deadline': timezone.now() + timedelta(days=30),
            },
            {
                'title': 'Website Redesign',
                'description': 'Redesign the main website with new branding',
                'status': 'active',
                'deadline': timezone.now() + timedelta(days=45),
            },
            {
                'title': 'API Integration',
                'description': 'Integrate with third-party APIs',
                'status': 'active',
                'deadline': timezone.now() + timedelta(days=15),
            },
        ]

        projects = []
        for project_data in projects_data:
            project, created = Project.objects.get_or_create(
                title=project_data['title'],
                defaults={
                    **project_data,
                    'created_by': users[0],
                }
            )
            if created:
                # Add team members
                project.team_members.set(random.sample(users, random.randint(2, 4)))
                self.stdout.write(f'Created project: {project.title}')
            projects.append(project)

        # Create tasks
        task_titles = [
            'Implement user authentication',
            'Design dashboard UI',
            'Write API documentation',
            'Setup database migrations',
            'Create user profile page',
            'Implement time tracking',
            'Add data visualization',
            'Setup CI/CD pipeline',
            'Write unit tests',
            'Performance optimization',
            'Security audit',
            'Mobile responsive design',
            'Email notifications',
            'Data backup system',
            'User feedback system',
        ]

        statuses = ['todo', 'in_progress', 'review', 'done']
        priorities = ['low', 'medium', 'high', 'urgent']

        for i, title in enumerate(task_titles):
            # Create tasks with past due dates for productivity analytics
            created_date = timezone.now() - timedelta(days=random.randint(1, 30))
            due_date = created_date + timedelta(days=random.randint(1, 14))
            
            task, created = Task.objects.get_or_create(
                title=title,
                defaults={
                    'description': f'Task description for {title}',
                    'status': random.choice(statuses),
                    'priority': random.choice(priorities),
                    'project': random.choice(projects) if random.choice([True, False]) else None,
                    'assigned_to': random.choice(users) if random.choice([True, False]) else None,
                    'created_by': random.choice(users),
                    'due_date': due_date,
                    'estimated_hours': random.uniform(1, 8),
                    'actual_hours': random.uniform(0, 10),
                    'created_at': created_date,
                }
            )
            if created:
                self.stdout.write(f'Created task: {task.title}')

        # Create time entries
        tasks = Task.objects.all()
        for _ in range(50):  # Create 50 time entries
            task = random.choice(tasks)
            user = random.choice(users)
            
            # Create time entries over the past month
            start_time = timezone.now() - timedelta(
                days=random.randint(1, 30),
                hours=random.randint(8, 18),
                minutes=random.randint(0, 59)
            )
            duration = random.uniform(0.5, 8)  # 0.5 to 8 hours
            end_time = start_time + timedelta(hours=duration)
            
            time_entry, created = TimeEntry.objects.get_or_create(
                task=task,
                user=user,
                start_time=start_time,
                defaults={
                    'end_time': end_time,
                    'duration_hours': duration,
                    'description': f'Working on {task.title}',
                }
            )
            if created:
                self.stdout.write(f'Created time entry: {user.name} - {task.title}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )