# Tasks Module

The **Tasks** module provides a complete task management system for the Habit Tracker RPG. It allows users to create, track, and complete three types of tasks: Habits, Dailies, and Todos. Each task type integrates with the RPG mechanics to reward (or penalize) users based on their behavior.

## Features

### Task Types

1. **Habits** - Recurring behaviors that can be good or bad
   - Good habits: Completing them rewards EXP and increases strength
   - Bad habits: Performing them reduces HP and decreases strength
   - Status: active, inactive, completed
   - Strength progression: fragile → weak → stable → strong → unbreakable

2. **Dailies** - Tasks that repeat on a schedule
   - Repeat patterns: daily, weekly, monthly, yearly
   - Custom repeat intervals and units
   - Completing them rewards EXP and increases strength
   - Status tracking for reset cycles

3. **Todos** - One-time tasks with due dates
   - Due date validation (must be today or future)
   - Completion status tracking
   - Highest EXP reward (20 points)
   - Filterable by active, planned, or completed status

### RPG Mechanics

**EXP Rewards:**
- Good Habit: +10 EXP
- Daily Task: +15 EXP
- Todo Task: +20 EXP

**HP Penalties:**
- Bad Habit: -5 HP

**Strength Progression:**
- Completing tasks increases strength by one level
- Performing bad habits decreases strength by one level
- Levels: fragile → weak → stable → strong → unbreakable

**Leveling System:**
- EXP needed per level: 100 × current_level
- On level up: Full HP restore + max HP +10

## API Endpoints

### Habits

```
GET    /api/tasks/habits/              - List all habits
POST   /api/tasks/habits/              - Create a habit
GET    /api/tasks/habits/{id}/         - Retrieve habit details
PATCH  /api/tasks/habits/{id}/         - Update a habit
DELETE /api/tasks/habits/{id}/         - Delete a habit
POST   /api/tasks/habits/{id}/complete/ - Complete/record habit
```

### Dailies

```
GET    /api/tasks/dailies/              - List all dailies
POST   /api/tasks/dailies/              - Create a daily
GET    /api/tasks/dailies/{id}/         - Retrieve daily details
PATCH  /api/tasks/dailies/{id}/         - Update a daily
DELETE /api/tasks/dailies/{id}/         - Delete a daily
POST   /api/tasks/dailies/{id}/complete/ - Complete daily
```

### Todos

```
GET    /api/tasks/todos/              - List all todos
POST   /api/tasks/todos/              - Create a todo
GET    /api/tasks/todos/{id}/         - Retrieve todo details
PATCH  /api/tasks/todos/{id}/         - Update a todo
DELETE /api/tasks/todos/{id}/         - Delete a todo
POST   /api/tasks/todos/{id}/complete/ - Complete todo
```

## Filtering & Search

All list endpoints support:
- **Filtering**: By type, status, strength, completion state
- **Search**: Full-text search in name and notes fields
- **Ordering**: Sort by any field (prefix with `-` for descending)

### Examples

```bash
# Filter good habits
GET /api/tasks/habits/?type=good

# Filter active habits with stable strength
GET /api/tasks/habits/?status=active&strength=stable

# Search for "water" in habits
GET /api/tasks/habits/?search=water

# Get active (incomplete) todos
GET /api/tasks/todos/?filter=active

# Get completed todos
GET /api/tasks/todos/?filter=completed

# Get planned todos (future due date, not completed)
GET /api/tasks/todos/?filter=planned

# Filter dailies by repeat pattern
GET /api/tasks/dailies/?repeats=daily

# Order todos by due date (ascending)
GET /api/tasks/todos/?ordering=due_date
```

## Models

### BaseTask (Abstract)
Base model shared by all task types:
- `user` - Foreign key to User
- `name` - Task name (max 100 chars)
- `notes` - Additional notes (optional)
- `strength` - Task strength level (default: stable)
- `created_at` - Timestamp

### Habit
- `type` - good or bad
- `status` - active, inactive, or completed

### Daily
- `repeats` - daily, weekly, monthly, yearly
- `repeat_on` - monday-sunday or everyday
- `repeat_interval` - Number of units between repeats
- `repeat_unit` - days, weeks, or months
- `status` - active, inactive, or completed

### Todo
- `due_date` - Date the task is due (validated)
- `is_completed` - Completion status

## Serializers

- `HabitSerializer` - Full CRUD for habits
- `DailySerializer` - Full CRUD for dailies
- `TodoSerializer` - Full CRUD for todos with due_date validation

All serializers:
- Enforce read-only fields: `id`, `created_at`, `user`
- Apply default values automatically
- Validate required fields
- Prevent past due dates (Todos)

## ViewSets

- `HabitViewSet` - CRUD + complete action
- `DailyViewSet` - CRUD + complete action
- `TodoViewSet` - CRUD + complete action

**Permissions:**
- All endpoints require JWT authentication
- Users can only access their own tasks

**Features:**
- Django Filter integration for advanced filtering
- Search support (name, notes)
- Custom ordering
- Atomic transactions for completion actions

## Admin Interface

All task models are registered in Django Admin with:
- List display with key fields
- Filtering by type, status, strength, dates
- Search by name, notes, username
- Read-only timestamp fields

## Testing

### Test Coverage

**56 tests total:**
- 9 model tests
- 15 serializer tests
- 32 view/API tests

**Model Tests** (`test_models.py`):
- Creation and validation
- String representations
- Default values
- Due date validation (Todo)

**Serializer Tests** (`test_serializers.py`):
- Valid data serialization
- Missing required fields
- Read-only field protection
- Default value application
- Due date validation (Todo)
- Update operations

**View Tests** (`test_views.py`):
- Authentication requirements
- User isolation (can only see own tasks)
- CRUD operations
- Completion actions with RPG mechanics
- Filtering (type, status, strength, completion)
- Search functionality
- Error handling (already completed, past dates)

### Running Tests

```bash
# Run all tasks tests
pytest tasks/tests/ -v

# Run specific test file
pytest tasks/tests/test_models.py -v
pytest tasks/tests/test_serializers.py -v
pytest tasks/tests/test_views.py -v

# Run with coverage
pytest tasks/tests/ --cov=tasks --cov-report=html
```

## Example Usage

### Create and Complete a Good Habit

```python
import requests

# Authenticate
login_response = requests.post('http://localhost:8000/api/users/login/', json={
    'username': 'myuser',
    'password': 'mypassword'
})
token = login_response.json()['access']
headers = {'Authorization': f'Bearer {token}'}

# Create habit
habit_data = {
    'name': 'Morning Meditation',
    'notes': '10 minutes',
    'type': 'good'
}
habit_response = requests.post(
    'http://localhost:8000/api/tasks/habits/',
    json=habit_data,
    headers=headers
)
habit_id = habit_response.json()['id']

# Complete habit
complete_response = requests.post(
    f'http://localhost:8000/api/tasks/habits/{habit_id}/complete/',
    headers=headers
)

# Response includes updated user stats
print(complete_response.json())
# {
#   "detail": "Good habit completed! +10 EXP",
#   "habit": {...},
#   "user": {
#     "current_hp": 20,
#     "max_hp": 20,
#     "current_exp": 10,
#     "current_level": 1
#   }
# }
```

### Create a Todo with Due Date

```python
from datetime import date, timedelta

tomorrow = (date.today() + timedelta(days=1)).isoformat()

todo_data = {
    'name': 'Buy groceries',
    'notes': 'Milk, eggs, bread',
    'due_date': tomorrow
}

todo_response = requests.post(
    'http://localhost:8000/api/tasks/todos/',
    json=todo_data,
    headers=headers
)
```

## Database Schema

```sql
-- Habits table
CREATE TABLE tasks_habit (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users_user(id),
    name VARCHAR(100) NOT NULL,
    notes TEXT,
    type VARCHAR(15) NOT NULL,  -- 'good' or 'bad'
    status VARCHAR(15) DEFAULT 'active',
    strength VARCHAR(15) DEFAULT 'stable',
    created_at TIMESTAMP WITH TIME ZONE
);

-- Dailies table
CREATE TABLE tasks_daily (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users_user(id),
    name VARCHAR(100) NOT NULL,
    notes TEXT,
    repeats VARCHAR(15) DEFAULT 'daily',
    repeat_on VARCHAR(15) DEFAULT 'everyday',
    repeat_interval INTEGER DEFAULT 1,
    repeat_unit VARCHAR(15) DEFAULT 'days',
    status VARCHAR(15) DEFAULT 'active',
    strength VARCHAR(15) DEFAULT 'stable',
    created_at TIMESTAMP WITH TIME ZONE
);

-- Todos table
CREATE TABLE tasks_todo (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users_user(id),
    name VARCHAR(100) NOT NULL,
    notes TEXT,
    due_date DATE NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    strength VARCHAR(15) DEFAULT 'stable',
    created_at TIMESTAMP WITH TIME ZONE
);
```

## Future Enhancements

Planned features for upcoming versions:
- [ ] Automatic daily reset (Celery background task)
- [ ] Streak tracking (consecutive completions)
- [ ] Habit strength decay for missed dailies
- [ ] Task categories/tags
- [ ] Task templates
- [ ] Recurring todos
- [ ] Batch operations
- [ ] Task history and analytics
- [ ] Push notifications/reminders
- [ ] Shared/team tasks
- [ ] Task difficulty levels (affects EXP rewards)

## Dependencies

- Django >= 5.2
- djangorestframework >= 3.16
- django-filter >= 24.0
- djangorestframework-simplejwt >= 5.4 (for authentication)

## Contributing

When adding new features:
1. Update models and migrations if needed
2. Add/update serializers with proper validation
3. Implement ViewSet logic with atomic transactions
4. Add comprehensive tests (models, serializers, views)
5. Update API documentation
6. Register new models in admin.py

## Documentation

- [API_DOCS.md](./API_DOCS.md) - Complete API documentation with examples
- [PROJECT_PLAN.md](../PROJECT_PLAN.md) - Overall project architecture
- [CHANGELOG.md](../CHANGELOG.md) - Version history

## License

Part of the Habit Tracker RPG project.