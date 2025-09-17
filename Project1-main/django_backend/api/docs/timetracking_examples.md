# Time Tracking API Examples

## Authentication

First, obtain a JWT token:

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "yourpassword"}'
```

Response:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

Store the access token for use in subsequent requests.

## Start a Timer

Start a timer for a specific task:

```bash
curl -X POST http://localhost:8000/api/tasks/123e4567-e89b-12d3-a456-426614174000/timer/start/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "task": "123e4567-e89b-12d3-a456-426614174000",
  "task_title": "Implement login page",
  "user": "098f6bcd-4621-3373-8ade-4e832627b4f6",
  "user_name": "John Doe",
  "start_time": "2023-07-10T09:30:00Z",
  "end_time": null,
  "duration_seconds": null,
  "created_at": "2023-07-10T09:30:00Z",
  "updated_at": "2023-07-10T09:30:00Z"
}
```

## Stop a Timer

Stop the active timer for a task:

```bash
curl -X POST http://localhost:8000/api/tasks/123e4567-e89b-12d3-a456-426614174000/timer/stop/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "task": "123e4567-e89b-12d3-a456-426614174000",
  "task_title": "Implement login page",
  "user": "098f6bcd-4621-3373-8ade-4e832627b4f6",
  "user_name": "John Doe",
  "start_time": "2023-07-10T09:30:00Z",
  "end_time": "2023-07-10T10:45:00Z",
  "duration_seconds": 4500,
  "created_at": "2023-07-10T09:30:00Z",
  "updated_at": "2023-07-10T10:45:00Z"
}
```

## Get Daily Timesheet

Retrieve a daily timesheet summary:

```bash
curl -X GET "http://localhost:8000/api/timesheets/daily/?date=2023-07-10" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

Response:
```json
{
  "date": "2023-07-10",
  "total_duration_seconds": 14400,
  "total_duration_formatted": "4 hours",
  "entries": [
    {
      "task_id": "123e4567-e89b-12d3-a456-426614174000",
      "task_title": "Implement login page",
      "project_id": "abcdef12-3456-7890-abcd-ef1234567890",
      "project_title": "Website Redesign",
      "total_duration_seconds": 4500,
      "total_duration_formatted": "1 hour 15 minutes"
    },
    {
      "task_id": "123e4567-e89b-12d3-a456-426614174001",
      "task_title": "Design database schema",
      "project_id": "abcdef12-3456-7890-abcd-ef1234567890",
      "project_title": "Website Redesign",
      "total_duration_seconds": 9900,
      "total_duration_formatted": "2 hours 45 minutes"
    }
  ]
}
```

## Get Weekly Timesheet

Retrieve a weekly timesheet summary:

```bash
curl -X GET "http://localhost:8000/api/timesheets/weekly/?week_start=2023-07-10" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

Response:
```json
{
  "week_start": "2023-07-10",
  "week_end": "2023-07-16",
  "total_duration_seconds": 108000,
  "total_duration_formatted": "30 hours",
  "entries": [
    {
      "task_id": "123e4567-e89b-12d3-a456-426614174000",
      "task_title": "Implement login page",
      "project_id": "abcdef12-3456-7890-abcd-ef1234567890",
      "project_title": "Website Redesign",
      "total_duration_seconds": 28800,
      "total_duration_formatted": "8 hours"
    },
    {
      "task_id": "123e4567-e89b-12d3-a456-426614174001",
      "task_title": "Design database schema",
      "project_id": "abcdef12-3456-7890-abcd-ef1234567890",
      "project_title": "Website Redesign",
      "total_duration_seconds": 43200,
      "total_duration_formatted": "12 hours"
    },
    {
      "task_id": "123e4567-e89b-12d3-a456-426614174002",
      "task_title": "Implement user authentication",
      "project_id": "abcdef12-3456-7890-abcd-ef1234567891",
      "project_title": "Mobile App",
      "total_duration_seconds": 36000,
      "total_duration_formatted": "10 hours"
    }
  ]
}
```