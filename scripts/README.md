# Scripts

This folder contains utility scripts for testing and development.

## Available Scripts

### `test_tasks_api.py`

A manual API testing script that demonstrates all Tasks module endpoints.

**Purpose:**
- Demonstrates the complete Tasks API workflow
- Useful for manual testing and verification
- Shows example API calls for all endpoints

**Requirements:**
```bash
pip install requests
```

**Usage:**
```bash
# Make sure the development server is running
python manage.py runserver

# In another terminal
python scripts/test_tasks_api.py
```

**What it does:**
1. Registers a test user
2. Logs in and obtains JWT token
3. Creates habits (good and bad)
4. Creates daily tasks
5. Creates todos
6. Completes tasks and shows EXP/HP rewards
7. Demonstrates filtering and search
8. Tests validation (e.g., past due dates)

**Note:** This is NOT a pytest test file. It's a manual testing script that makes real HTTP requests to your running Django server.

## Adding New Scripts

When adding new scripts:
1. Use descriptive names
2. Add documentation in this README
3. Include requirements and usage instructions
4. If the script name starts with `test_`, make sure pytest ignores the `scripts/` folder (already configured in `pytest.ini`)

## Development Scripts (Future)

Planned scripts:
- `seed_database.py` - Populate database with test data
- `generate_test_users.py` - Create multiple test users
- `reset_user_progress.py` - Reset user stats for testing
- `export_data.py` - Export user data for backup
- `check_health.py` - API health check script