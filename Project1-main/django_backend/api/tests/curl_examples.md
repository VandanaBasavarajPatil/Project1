# Role-Based Permission Examples

## Authentication

First, obtain an authentication token:

```bash
# Login as Scrum Master
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "scrummaster@example.com", "password": "password123"}'

# Login as Employee
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "employee@example.com", "password": "password123"}'
```

## Project Permissions

### Create Project (Scrum Master Only)

```bash
# Scrum Master can create projects (Success - 201)
curl -X POST http://localhost:8000/api/projects/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <scrum_master_token>" \
  -d '{"name": "New Project", "description": "Project description", "status": "active"}'

# Employee cannot create projects (Forbidden - 403)
curl -X POST http://localhost:8000/api/projects/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <employee_token>" \
  -d '{"name": "New Project", "description": "Project description", "status": "active"}'
```

### Update Project (Scrum Master Only)

```bash
# Scrum Master can update projects (Success - 200)
curl -X PATCH http://localhost:8000/api/projects/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <scrum_master_token>" \
  -d '{"name": "Updated Project Name"}'

# Employee cannot update projects (Forbidden - 403)
curl -X PATCH http://localhost:8000/api/projects/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <employee_token>" \
  -d '{"name": "Updated Project Name"}'
```

## Task Permissions

### Create Task (Project Members)

```bash
# Project member can create tasks (Success - 201)
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <employee_token>" \
  -d '{"title": "New Task", "description": "Task description", "status": "todo", "priority": "medium", "project": 1}'

# Non-project member cannot create tasks (Forbidden - 403)
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <non_member_token>" \
  -d '{"title": "New Task", "description": "Task description", "status": "todo", "priority": "medium", "project": 1}'
```

### Update Task Status (Assignee or Scrum Master)

```bash
# Assignee can update task status (Success - 200)
curl -X PATCH http://localhost:8000/api/tasks/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <assignee_token>" \
  -d '{"status": "in_progress"}'

# Non-assignee cannot update task status (Forbidden - 403)
curl -X PATCH http://localhost:8000/api/tasks/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <non_assignee_token>" \
  -d '{"status": "in_progress"}'

# Scrum Master can update any task (Success - 200)
curl -X PATCH http://localhost:8000/api/tasks/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <scrum_master_token>" \
  -d '{"status": "done"}'
```

### Delete Task (Scrum Master Only)

```bash
# Scrum Master can delete tasks (Success - 204)
curl -X DELETE http://localhost:8000/api/tasks/1/ \
  -H "Authorization: Bearer <scrum_master_token>"

# Employee cannot delete tasks (Forbidden - 403)
curl -X DELETE http://localhost:8000/api/tasks/1/ \
  -H "Authorization: Bearer <employee_token>"
```

## Comments Permissions

```bash
# Project member can comment on tasks (Success - 201)
curl -X POST http://localhost:8000/api/tasks/1/comments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <member_token>" \
  -d '{"content": "This is a comment"}'

# Non-project member cannot comment (Forbidden - 403)
curl -X POST http://localhost:8000/api/tasks/1/comments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <non_member_token>" \
  -d '{"content": "This is a comment"}'
```