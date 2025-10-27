# Tasks API Documentation

## Overview

The Tasks module provides full CRUD operations for managing three types of tasks in the Habit Tracker RPG:
- **Habits**: Recurring behaviors (good or bad) that affect character stats
- **Dailies**: Tasks that repeat on a schedule (daily, weekly, monthly, yearly)
- **Todos**: One-time tasks with due dates

All endpoints require JWT authentication. Users can only access their own tasks.

## Base URL

```
/api/tasks/
```

---

## Habits

### List Habits

**GET** `/api/tasks/habits/`

Returns a list of all habits for the authenticated user.

**Query Parameters:**
- `type` (optional): Filter by habit type (`good`, `bad`)
- `status` (optional): Filter by status (`active`, `inactive`, `completed`)
- `strength` (optional): Filter by strength (`fragile`, `weak`, `stable`, `strong`, `unbreakable`)
- `search` (optional): Search in name and notes fields
- `ordering` (optional): Order by field (prefix with `-` for descending)

**Example Request:**
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "http://localhost:8000/api/tasks/habits/?type=good&status=active"
```

**Example Response:**
```json
[
  {
    "id": 1,
    "user": 5,
    "name": "Drink Water",
    "notes": "8 glasses per day",
    "type": "good",
    "status": "active",
    "strength": "stable",
    "created_at": "2025-10-27T10:30:00Z"
  }
]
```

---

### Create Habit

**POST** `/api/tasks/habits/`

Creates a new habit for the authenticated user.

**Request Body:**
```json
{
  "name": "Morning Exercise",
  "notes": "30 minutes of cardio",
  "type": "good",
  "status": "active",
  "strength": "stable"
}
```

**Required Fields:**
- `name` (string, max 100 chars)
- `type` (string: `good` or `bad`)

**Optional Fields:**
- `notes` (string)
- `status` (string: `active`, `inactive`, `completed`, default: `active`)
- `strength` (string: `fragile`, `weak`, `stable`, `strong`, `unbreakable`, default: `stable`)

**Response:** `201 Created`
```json
{
  "id": 2,
  "user": 5,
  "name": "Morning Exercise",
  "notes": "30 minutes of cardio",
  "type": "good",
  "status": "active",
  "strength": "stable",
  "created_at": "2025-10-27T11:00:00Z"
}
```

---

### Retrieve Habit

**GET** `/api/tasks/habits/{id}/`

Returns details of a specific habit.

**Example Response:**
```json
{
  "id": 1,
  "user": 5,
  "name": "Drink Water",
  "notes": "8 glasses per day",
  "type": "good",
  "status": "active",
  "strength": "stable",
  "created_at": "2025-10-27T10:30:00Z"
}
```

---

### Update Habit

**PATCH** `/api/tasks/habits/{id}/`

Partially updates a habit. Can also use **PUT** for full updates.

**Request Body (partial):**
```json
{
  "name": "Drink More Water",
  "status": "inactive"
}
```

**Response:** `200 OK` (updated habit object)

---

### Delete Habit

**DELETE** `/api/tasks/habits/{id}/`

Deletes a habit permanently.

**Response:** `204 No Content`

---

### Complete Habit

**POST** `/api/tasks/habits/{id}/complete/`

Records completion of a habit and applies RPG mechanics.

**Good Habit Effects:**
- User gains +10 EXP
- Habit strength increases by one level
- Message: "Good habit completed! +10 EXP"

**Bad Habit Effects:**
- User loses -5 HP (minimum 0)
- Habit strength decreases by one level
- Message: "Bad habit recorded. -5 HP"

**Example Response:**
```json
{
  "detail": "Good habit completed! +10 EXP",
  "habit": {
    "id": 1,
    "user": 5,
    "name": "Drink Water",
    "type": "good",
    "strength": "strong",
    "created_at": "2025-10-27T10:30:00Z"
  },
  "user": {
    "current_hp": 20,
    "max_hp": 20,
    "current_exp": 110,
    "current_level": 2
  }
}
```

---

## Dailies

### List Dailies

**GET** `/api/tasks/dailies/`

Returns a list of all daily tasks for the authenticated user.

**Query Parameters:**
- `status` (optional): Filter by status (`active`, `inactive`, `completed`)
- `repeats` (optional): Filter by repeat pattern (`daily`, `weekly`, `monthly`, `yearly`)
- `repeat_on` (optional): Filter by day (`monday`, `tuesday`, ..., `sunday`, `everyday`)
- `search` (optional): Search in name and notes fields
- `ordering` (optional): Order by field

**Example Response:**
```json
[
  {
    "id": 1,
    "user": 5,
    "name": "Morning Meditation",
    "notes": "15 minutes",
    "strength": "stable",
    "status": "active",
    "repeats": "daily",
    "repeat_on": "everyday",
    "repeat_interval": 1,
    "repeat_unit": "days",
    "created_at": "2025-10-27T08:00:00Z"
  }
]
```

---

### Create Daily

**POST** `/api/tasks/dailies/`

Creates a new daily task.

**Request Body:**
```json
{
  "name": "Evening Yoga",
  "notes": "20 minutes before bed",
  "repeats": "daily",
  "repeat_on": "everyday",
  "repeat_interval": 1,
  "repeat_unit": "days"
}
```

**Required Fields:**
- `name` (string, max 100 chars)

**Optional Fields:**
- `notes` (string)
- `strength` (string, default: `stable`)
- `status` (string, default: `active`)
- `repeats` (string, default: `daily`)
- `repeat_on` (string, default: `everyday`)
- `repeat_interval` (integer, default: 1)
- `repeat_unit` (string, default: `days`)

**Response:** `201 Created`

---

### Retrieve Daily

**GET** `/api/tasks/dailies/{id}/`

Returns details of a specific daily task.

---

### Update Daily

**PATCH** `/api/tasks/dailies/{id}/`

Partially updates a daily task.

---

### Delete Daily

**DELETE** `/api/tasks/dailies/{id}/`

Deletes a daily task permanently.

**Response:** `204 No Content`

---

### Complete Daily

**POST** `/api/tasks/dailies/{id}/complete/`

Marks a daily task as completed and applies RPG mechanics.

**Effects:**
- User gains +15 EXP
- Daily strength increases by one level
- Status changed to `completed`
- Message: "Daily task completed! +15 EXP"

**Error Conditions:**
- If already completed: `400 Bad Request` with message "Daily task already completed for today."

**Example Response:**
```json
{
  "detail": "Daily task completed! +15 EXP",
  "daily": {
    "id": 1,
    "user": 5,
    "name": "Morning Meditation",
    "status": "completed",
    "strength": "strong",
    "created_at": "2025-10-27T08:00:00Z"
  },
  "user": {
    "current_hp": 20,
    "max_hp": 20,
    "current_exp": 125,
    "current_level": 2
  }
}
```

---

## Todos

### List Todos

**GET** `/api/tasks/todos/`

Returns a list of all todo tasks for the authenticated user.

**Query Parameters:**
- `is_completed` (optional): Filter by completion status (`true`, `false`)
- `filter` (optional): Special filters:
  - `active` - Returns incomplete todos
  - `completed` - Returns completed todos
  - `planned` - Returns incomplete todos with future due dates
- `search` (optional): Search in name and notes fields
- `ordering` (optional): Order by field (default: `due_date`, `-created_at`)

**Example Request:**
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "http://localhost:8000/api/tasks/todos/?filter=active"
```

**Example Response:**
```json
[
  {
    "id": 1,
    "user": 5,
    "name": "Complete project report",
    "notes": "Due by Friday",
    "strength": "stable",
    "due_date": "2025-10-30",
    "is_completed": false,
    "created_at": "2025-10-27T09:00:00Z"
  }
]
```

---

### Create Todo

**POST** `/api/tasks/todos/`

Creates a new todo task.

**Request Body:**
```json
{
  "name": "Buy groceries",
  "notes": "Milk, bread, eggs",
  "due_date": "2025-10-28"
}
```

**Required Fields:**
- `name` (string, max 100 chars)
- `due_date` (string, ISO date format: `YYYY-MM-DD`)

**Optional Fields:**
- `notes` (string)
- `strength` (string, default: `stable`)
- `is_completed` (boolean, default: `false`)

**Validation:**
- `due_date` cannot be in the past (must be today or future)

**Response:** `201 Created`

**Error Response (past due date):**
```json
{
  "due_date": ["Due date cannot be in the past."]
}
```

---

### Retrieve Todo

**GET** `/api/tasks/todos/{id}/`

Returns details of a specific todo.

---

### Update Todo

**PATCH** `/api/tasks/todos/{id}/`

Partially updates a todo task.

**Request Body:**
```json
{
  "name": "Buy groceries ASAP",
  "is_completed": true
}
```

---

### Delete Todo

**DELETE** `/api/tasks/todos/{id}/`

Deletes a todo permanently.

**Response:** `204 No Content`

---

### Complete Todo

**POST** `/api/tasks/todos/{id}/complete/`

Marks a todo as completed and applies RPG mechanics.

**Effects:**
- User gains +20 EXP
- Todo strength increases by one level
- `is_completed` set to `true`
- Message: "Todo completed! +20 EXP"

**Error Conditions:**
- If already completed: `400 Bad Request` with message "Todo already completed."

**Example Response:**
```json
{
  "detail": "Todo completed! +20 EXP",
  "todo": {
    "id": 1,
    "user": 5,
    "name": "Complete project report",
    "due_date": "2025-10-30",
    "is_completed": true,
    "strength": "strong",
    "created_at": "2025-10-27T09:00:00Z"
  },
  "user": {
    "current_hp": 20,
    "max_hp": 20,
    "current_exp": 145,
    "current_level": 2
  }
}
```

---

## Authentication

All endpoints require JWT authentication. Include the access token in the `Authorization` header:

```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Obtaining Tokens:**
- Login: `POST /api/users/login/`
- Refresh: `POST /api/users/refresh/`

---

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 400 Bad Request
```json
{
  "field_name": ["Error message describing the issue."]
}
```

---

## Strength Progression

Task strength levels (from weakest to strongest):
1. `fragile`
2. `weak`
3. `stable` (default)
4. `strong`
5. `unbreakable`

**Strength Changes:**
- Completing good habits, dailies, or todos **increases** strength by one level
- Performing bad habits **decreases** strength by one level
- Strength cannot go below `fragile` or above `unbreakable`

---

## EXP and Level System

**EXP Rewards:**
- Good Habit: +10 EXP
- Daily Task: +15 EXP
- Todo Task: +20 EXP
- Bad Habit: No EXP (penalty: -5 HP)

**Leveling Up:**
- Formula: `100 × current_level` EXP needed per level
- Level 1 → 2: 100 EXP
- Level 2 → 3: 200 EXP
- Level 3 → 4: 300 EXP
- On level up: HP fully restored, max HP +10

---

## Pagination

By default, list endpoints return all results. For future scalability, consider implementing pagination:

```
?page=1&page_size=20
```

---

## Rate Limiting

Standard API rate limits apply (configured in `settings.py`):
- Authenticated users: 30 requests/minute
- Anonymous users: 10 requests/minute

---

## Examples

### Complete Workflow: Creating and Completing a Habit

**1. Create a good habit:**
```bash
curl -X POST http://localhost:8000/api/tasks/habits/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Read 30 minutes",
    "type": "good",
    "notes": "Read before bed"
  }'
```

**2. Complete the habit:**
```bash
curl -X POST http://localhost:8000/api/tasks/habits/1/complete/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**3. Check updated user stats:**
```bash
curl http://localhost:8000/api/users/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Future Enhancements

Planned features for upcoming versions:
- Automatic daily reset (Celery task)
- Streak tracking
- Habit strength decay for missed dailies
- Recurring todo tasks
- Task templates and categories
- Team/shared tasks
- Notifications and reminders

---

## Support

For issues or questions, contact the development team or open an issue on the project repository.