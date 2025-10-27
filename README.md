# Habit Tracker RPG

A Django REST Framework-based habit tracking application with RPG mechanics. Track your habits, dailies, and todos while leveling up your character!

[![CI Status](https://github.com/USER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/USER/REPO/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/USER/REPO/badge.svg)](https://codecov.io/gh/USER/REPO)

## 🎮 Features

### ✅ Completed Modules

#### **Users Module** (v0.3.0)
- JWT-based authentication (register, login, logout, token refresh)
- User profiles with RPG attributes (HP, EXP, Level)
- Avatar upload with validation
- Password change with token blacklisting
- Case-insensitive email uniqueness
- Comprehensive test suite (33 tests)

#### **Tasks Module** (v0.5.0) ⭐ NEW
- **Habits**: Track good and bad recurring behaviors
  - Good habits: +10 EXP, increase strength
  - Bad habits: -5 HP, decrease strength
- **Dailies**: Recurring tasks with flexible schedules
  - Daily, weekly, monthly, yearly patterns
  - +15 EXP per completion
- **Todos**: One-time tasks with due dates
  - +20 EXP per completion
  - Due date validation
- Full CRUD API with filtering, search, and ordering
- RPG mechanics integration (EXP, HP, leveling)
- Comprehensive test suite (56 tests)

### 🚧 Planned Modules

- **Inventory**: Equipment and items system
- **Estate**: Build your homestead for passive bonuses
- **Economy**: Shop, marketplace, resources
- **Quests**: Daily, weekly, and special quests
- **Challenges**: Personal and community challenges
- **Support**: Help desk and FAQ

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/USER/REPO.git
cd HT_RPG

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Environment Variables

Create a `.env` file in the project root:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.postgresql
DB_NAME=htrpg_db
DB_USER=htrpg_user
DB_PASSWORD=htrpg
DB_HOST=localhost
DB_PORT=5432
```

## 📚 API Documentation

### Authentication

```bash
# Register
POST /api/users/register/
{
  "username": "player1",
  "email": "player1@example.com",
  "password": "SecurePass123!"
}

# Login
POST /api/users/login/
{
  "username": "player1",
  "password": "SecurePass123!"
}

# Get profile
GET /api/users/profile/
Authorization: Bearer <access_token>
```

### Tasks

```bash
# Create a good habit
POST /api/tasks/habits/
Authorization: Bearer <access_token>
{
  "name": "Drink Water",
  "type": "good",
  "notes": "8 glasses per day"
}

# Complete a habit (earn EXP!)
POST /api/tasks/habits/{id}/complete/
Authorization: Bearer <access_token>

# List all habits
GET /api/tasks/habits/
Authorization: Bearer <access_token>

# Filter good habits
GET /api/tasks/habits/?type=good
Authorization: Bearer <access_token>

# Create a daily task
POST /api/tasks/dailies/
Authorization: Bearer <access_token>
{
  "name": "Morning Exercise",
  "repeats": "daily"
}

# Create a todo
POST /api/tasks/todos/
Authorization: Bearer <access_token>
{
  "name": "Complete project",
  "due_date": "2025-10-30"
}
```

For complete API documentation, see:
- [Tasks API Documentation](tasks/API_DOCS.md)
- [Quick Start Guide](QUICKSTART_TASKS.md)

## 🧪 Testing

### Run All Tests

```bash
# Quick test run
pytest -q

# Verbose output
pytest -v

# Run specific module
pytest users/tests/ -v
pytest tasks/tests/ -v

# With coverage
pytest --cov=users --cov=tasks --cov-report=html
```

### Test Coverage

Current test statistics:
- **Users**: 33 tests ✅
- **Tasks**: 56 tests ✅
- **Total**: 89 tests ✅

Target coverage: 85%+

## 🎯 RPG Mechanics

### Experience & Leveling

- **Level Formula**: 100 × current_level EXP needed per level
- **Level Up**: Fully restores HP + increases max HP by 10

### EXP Rewards

| Action | EXP Gained |
|--------|------------|
| Complete Good Habit | +10 |
| Complete Daily Task | +15 |
| Complete Todo | +20 |

### HP System

| Action | HP Change |
|--------|-----------|
| Perform Bad Habit | -5 |
| Level Up | Full restore + max HP +10 |

### Strength Progression

Tasks have strength levels that increase with consistency:
1. Fragile
2. Weak
3. Stable (default)
4. Strong
5. Unbreakable

## 🛠️ Development

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

### Code Quality

- **Linting**: Ruff/Flake8
- **Formatting**: Black/isort
- **Type Checking**: Pyright (optional)

### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# View migration SQL
python manage.py sqlmigrate <app_name> <migration_number>
```

### Admin Interface

Access the Django admin at `http://localhost:8000/admin/`

All models are registered with custom list views and filters.

## 📦 Project Structure

```
HT_RPG/
├── habit_tracker_rpg/       # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/                   # User authentication & profiles
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests/
├── tasks/                   # Habits, dailies, todos
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── enums.py
│   ├── tests/
│   ├── API_DOCS.md
│   └── README.md
├── inventory/               # (Planned)
├── estate/                  # (Planned)
├── economy/                 # (Planned)
├── quests/                  # (Planned)
├── challenges/              # (Planned)
├── support/                 # (Planned)
├── media/                   # User uploads
├── manage.py
├── requirements.txt
├── pytest.ini
├── CHANGELOG.md
└── README.md
```

## 📖 Documentation

- [PROJECT_PLAN.md](PROJECT_PLAN.md) - Overall architecture and roadmap
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [QUICKSTART_TASKS.md](QUICKSTART_TASKS.md) - Get started with tasks in 5 minutes
- [tasks/API_DOCS.md](tasks/API_DOCS.md) - Complete Tasks API reference
- [tasks/README.md](tasks/README.md) - Tasks module documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Django & Django REST Framework communities
- Contributors and testers
- Habitica for inspiration

## 📞 Support

- Open an issue on GitHub
- Check the [documentation](PROJECT_PLAN.md)
- Review [API documentation](tasks/API_DOCS.md)

---

**Built with ❤️ using Django & DRF**
