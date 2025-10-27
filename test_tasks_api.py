"""
Manual API test script for tasks endpoints.
Run this after starting the development server: python manage.py runserver

Usage:
    python test_tasks_api.py
"""

import requests
import json
from datetime import date, timedelta

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"


def print_response(response, title="Response"):
    """Pretty print API response"""
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print(f"{'=' * 60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print(f"{'=' * 60}\n")


def test_tasks_api():
    """Test tasks API endpoints"""

    # Step 1: Register a test user
    print("🔧 Step 1: Registering test user...")
    register_data = {
        "username": "taskstester",
        "email": "tasks@test.com",
        "password": "SecurePass123!",
    }
    response = requests.post(f"{API_URL}/users/register/", json=register_data)
    print_response(response, "Register User")

    # Step 2: Login
    print("🔐 Step 2: Logging in...")
    login_data = {"username": "taskstester", "password": "SecurePass123!"}
    response = requests.post(f"{API_URL}/users/login/", json=login_data)
    print_response(response, "Login")

    if response.status_code != 200:
        print("❌ Login failed. Exiting.")
        return

    tokens = response.json()
    access_token = tokens["access"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Step 3: Check user profile
    print("👤 Step 3: Getting user profile...")
    response = requests.get(f"{API_URL}/users/profile/", headers=headers)
    print_response(response, "User Profile")

    # Step 4: Create a good habit
    print("✅ Step 4: Creating a good habit...")
    habit_data = {"name": "Drink Water", "notes": "8 glasses per day", "type": "good"}
    response = requests.post(
        f"{API_URL}/tasks/habits/", json=habit_data, headers=headers
    )
    print_response(response, "Create Good Habit")

    if response.status_code == 201:
        habit_id = response.json()["id"]
    else:
        habit_id = None

    # Step 5: Create a bad habit
    print("❌ Step 5: Creating a bad habit...")
    bad_habit_data = {"name": "Smoking", "notes": "Trying to quit", "type": "bad"}
    response = requests.post(
        f"{API_URL}/tasks/habits/", json=bad_habit_data, headers=headers
    )
    print_response(response, "Create Bad Habit")

    if response.status_code == 201:
        bad_habit_id = response.json()["id"]
    else:
        bad_habit_id = None

    # Step 6: List all habits
    print("📋 Step 6: Listing all habits...")
    response = requests.get(f"{API_URL}/tasks/habits/", headers=headers)
    print_response(response, "List Habits")

    # Step 7: Filter good habits
    print("🔍 Step 7: Filtering good habits...")
    response = requests.get(f"{API_URL}/tasks/habits/?type=good", headers=headers)
    print_response(response, "Filter Good Habits")

    # Step 8: Complete the good habit
    if habit_id:
        print("🎯 Step 8: Completing good habit...")
        response = requests.post(
            f"{API_URL}/tasks/habits/{habit_id}/complete/", headers=headers
        )
        print_response(response, "Complete Good Habit")

    # Step 9: Record bad habit
    if bad_habit_id:
        print("💔 Step 9: Recording bad habit...")
        response = requests.post(
            f"{API_URL}/tasks/habits/{bad_habit_id}/complete/", headers=headers
        )
        print_response(response, "Record Bad Habit")

    # Step 10: Create a daily task
    print("📅 Step 10: Creating a daily task...")
    daily_data = {
        "name": "Morning Exercise",
        "notes": "30 minutes cardio",
        "repeats": "daily",
        "repeat_on": "everyday",
    }
    response = requests.post(
        f"{API_URL}/tasks/dailies/", json=daily_data, headers=headers
    )
    print_response(response, "Create Daily Task")

    if response.status_code == 201:
        daily_id = response.json()["id"]
    else:
        daily_id = None

    # Step 11: Complete daily task
    if daily_id:
        print("✨ Step 11: Completing daily task...")
        response = requests.post(
            f"{API_URL}/tasks/dailies/{daily_id}/complete/", headers=headers
        )
        print_response(response, "Complete Daily Task")

    # Step 12: Create a todo
    print("📝 Step 12: Creating a todo...")
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    todo_data = {
        "name": "Complete project report",
        "notes": "Due by end of week",
        "due_date": tomorrow,
    }
    response = requests.post(f"{API_URL}/tasks/todos/", json=todo_data, headers=headers)
    print_response(response, "Create Todo")

    if response.status_code == 201:
        todo_id = response.json()["id"]
    else:
        todo_id = None

    # Step 13: List active todos
    print("📌 Step 13: Listing active todos...")
    response = requests.get(f"{API_URL}/tasks/todos/?filter=active", headers=headers)
    print_response(response, "List Active Todos")

    # Step 14: Complete todo
    if todo_id:
        print("🎉 Step 14: Completing todo...")
        response = requests.post(
            f"{API_URL}/tasks/todos/{todo_id}/complete/", headers=headers
        )
        print_response(response, "Complete Todo")

    # Step 15: Check final user stats
    print("🏆 Step 15: Checking final user stats...")
    response = requests.get(f"{API_URL}/users/profile/", headers=headers)
    print_response(response, "Final User Stats")

    # Step 16: Search tasks
    print("🔎 Step 16: Searching for 'water'...")
    response = requests.get(f"{API_URL}/tasks/habits/?search=water", headers=headers)
    print_response(response, "Search Results")

    # Step 17: Update a habit
    if habit_id:
        print("✏️ Step 17: Updating habit...")
        update_data = {"name": "Drink MORE Water", "status": "active"}
        response = requests.patch(
            f"{API_URL}/tasks/habits/{habit_id}/", json=update_data, headers=headers
        )
        print_response(response, "Update Habit")

    # Step 18: Test past due date validation
    print("⚠️ Step 18: Testing past due date (should fail)...")
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    invalid_todo = {"name": "Past Task", "due_date": yesterday}
    response = requests.post(
        f"{API_URL}/tasks/todos/", json=invalid_todo, headers=headers
    )
    print_response(response, "Create Todo with Past Date (Expected Error)")

    print("\n" + "=" * 60)
    print("✅ Tasks API Manual Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    print("\n🚀 Starting Tasks API Manual Test\n")
    print("Make sure the development server is running:")
    print("  python manage.py runserver\n")

    try:
        test_tasks_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("Please make sure the Django development server is running:")
        print("  python manage.py runserver")
    except Exception as e:
        print(f"\n❌ Error: {e}")
