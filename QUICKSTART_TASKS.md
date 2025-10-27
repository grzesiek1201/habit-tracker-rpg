# Quick Start Guide: Tasks Module

Get started with the Tasks API in 5 minutes!

## Prerequisites

- Django server running: `python manage.py runserver`
- User account created (or use the examples below)

## Step 1: Authentication

First, create an account and get your access token:

```bash
# Register
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "gamer123",
    "email": "gamer@example.com",
    "password": "SecurePass123!"
  }'

# Login
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "gamer123",
    "password": "SecurePass123!"
  }'
```

**Save your access token!** You'll need it for all subsequent requests.

```bash
export TOKEN="your_access_token_here"
```

## Step 2: Create Your First Habit

Create a good habit (e.g., drinking water):

```bash
curl -X POST http://localhost:8000/api/tasks/habits/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Drink Water",
    "notes": "8 glasses per day",
    "type": "good"
  }'
```

**Response:**
```json
{
  "id": 1,
  "user": 5,
  "name": "Drink Water",
  "notes": "8 glasses per day",
  "type": "good",
  "status": "active",
  "strength": "stable",
  "created_at": "2025-10-27T10:00:00Z"
}
```

## Step 3: Complete the Habit

Mark it as completed to earn EXP:

```bash
curl -X POST http://localhost:8000/api/tasks/habits/1/complete/ \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "detail": "Good habit completed! +10 EXP",
  "habit": {
    "id": 1,
    "name": "Drink Water",
    "strength": "strong"
  },
  "user": {
    "current_hp": 10,
    "max_hp": 10,
    "current_exp": 10,
    "current_level": 1
  }
}
```

🎉 **You just earned 10 EXP and increased your habit strength!**

## Step 4: Create a Daily Task

Daily tasks repeat every day:

```bash
curl -X POST http://localhost:8000/api/tasks/dailies/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Morning Exercise",
    "notes": "30 minutes of cardio",
    "repeats": "daily"
  }'
```

Complete it to earn **+15 EXP**:

```bash
curl -X POST http://localhost:8000/api/tasks/dailies/1/complete/ \
  -H "Authorization: Bearer $TOKEN"
```

## Step 5: Create a Todo

Todos are one-time tasks with due dates:

```bash
curl -X POST http://localhost:8000/api/tasks/todos/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Complete project report",
    "notes": "Due Friday",
    "due_date": "2025-10-30"
  }'
```

Complete it to earn **+20 EXP** (highest reward!):

```bash
curl -X POST http://localhost:8000/api/tasks/todos/1/complete/ \
  -H "Authorization: Bearer $TOKEN"
```

## Step 6: View All Your Tasks

### List all habits
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/tasks/habits/
```

### Filter good habits only
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/tasks/habits/?type=good"
```

### Search for specific tasks
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/tasks/habits/?search=water"
```

### List active todos
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/tasks/todos/?filter=active"
```

## Step 7: Check Your Progress

View your updated character stats:

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/users/profile/
```

**Response:**
```json
{
  "id": 5,
  "username": "gamer123",
  "current_hp": 10,
  "max_hp": 10,
  "current_exp": 45,
  "current_level": 1,
  "avatar_picture": null,
  "estate_bonus_hp": 0,
  "estate_bonus_exp": 0
}
```

## Understanding Rewards

| Task Type | EXP Reward | HP Change | Strength Change |
|-----------|------------|-----------|-----------------|
| Good Habit | +10 | 0 | ⬆️ Increase |
| Bad Habit | 0 | -5 | ⬇️ Decrease |
| Daily Task | +15 | 0 | ⬆️ Increase |
| Todo | +20 | 0 | ⬆️ Increase |

**Leveling Up:**
- Level 1 → 2: Need 100 EXP
- Level 2 → 3: Need 200 EXP
- Level 3 → 4: Need 300 EXP
- On level up: Full HP + max HP increases by 10

**Strength Levels:**
1. Fragile
2. Weak
3. Stable (default)
4. Strong
5. Unbreakable

## Common Use Cases

### Track a Bad Habit

Create a bad habit you want to break:

```bash
curl -X POST http://localhost:8000/api/tasks/habits/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Smoking",
    "notes": "Trying to quit",
    "type": "bad"
  }'
```

When you slip up, record it (loses 5 HP):

```bash
curl -X POST http://localhost:8000/api/tasks/habits/2/complete/ \
  -H "Authorization: Bearer $TOKEN"
```

### Create a Weekly Task

```bash
curl -X POST http://localhost:8000/api/tasks/dailies/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Grocery Shopping",
    "repeats": "weekly",
    "repeat_on": "sunday"
  }'
```

### Update a Task

```bash
curl -X PATCH http://localhost:8000/api/tasks/habits/1/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Drink MORE Water",
    "status": "active"
  }'
```

### Delete a Task

```bash
curl -X DELETE http://localhost:8000/api/tasks/habits/1/ \
  -H "Authorization: Bearer $TOKEN"
```

## Python Example

Want to use Python instead? Here's a complete example:

```python
import requests
from datetime import date, timedelta

BASE_URL = "http://localhost:8000/api"

# Login
response = requests.post(f"{BASE_URL}/users/login/", json={
    "username": "gamer123",
    "password": "SecurePass123!"
})
token = response.json()["access"]
headers = {"Authorization": f"Bearer {token}"}

# Create a habit
habit_data = {
    "name": "Read 30 minutes",
    "type": "good",
    "notes": "Before bed"
}
habit_response = requests.post(
    f"{BASE_URL}/tasks/habits/",
    json=habit_data,
    headers=headers
)
habit = habit_response.json()
print(f"Created habit: {habit['name']}")

# Complete the habit
complete_response = requests.post(
    f"{BASE_URL}/tasks/habits/{habit['id']}/complete/",
    headers=headers
)
result = complete_response.json()
print(f"{result['detail']}")
print(f"New EXP: {result['user']['current_exp']}")

# Create a todo
tomorrow = (date.today() + timedelta(days=1)).isoformat()
todo_data = {
    "name": "Finish homework",
    "due_date": tomorrow
}
todo_response = requests.post(
    f"{BASE_URL}/tasks/todos/",
    json=todo_data,
    headers=headers
)
print(f"Created todo: {todo_response.json()['name']}")

# List all tasks
habits = requests.get(f"{BASE_URL}/tasks/habits/", headers=headers).json()
print(f"\nYou have {len(habits)} habits")
```

## Testing Script

Want to test everything at once? Use our provided test script:

```bash
# Make sure server is running
python manage.py runserver

# In another terminal
python test_tasks_api.py
```

This will run through all the endpoints and show you the results!

## Tips & Tricks

1. **Start Small**: Begin with 2-3 habits and 1-2 dailies
2. **Be Consistent**: Complete tasks daily to build streaks (coming soon!)
3. **Use Filters**: Filter by status to focus on active tasks only
4. **Search**: Use search to quickly find specific tasks
5. **Strength Matters**: Higher strength tasks are more valuable (future feature)
6. **Level Up Strategy**: Complete todos (20 EXP) when close to leveling up

## Troubleshooting

**401 Unauthorized?**
- Check your token is valid
- Token might be expired (login again to get a new one)

**400 Bad Request?**
- Check required fields (name, type for habits, due_date for todos)
- Ensure due_date is not in the past

**404 Not Found?**
- Verify the task ID exists
- Make sure it belongs to your user

**Can't see tasks?**
- Tasks are user-specific - you can only see your own

## Next Steps

- 📖 Read the full [API Documentation](tasks/API_DOCS.md)
- 🧪 Run the test suite: `pytest tasks/tests/ -v`
- 🏗️ Explore the [Tasks README](tasks/README.md)
- 🎮 Check out other modules: Inventory, Estate, Economy (coming soon!)

## Need Help?

- Check the [API_DOCS.md](tasks/API_DOCS.md) for detailed endpoint documentation
- Look at test files in `tasks/tests/` for more examples
- Review the [PROJECT_PLAN.md](PROJECT_PLAN.md) for the overall architecture

---

**Happy Habit Tracking! 🎮✨**