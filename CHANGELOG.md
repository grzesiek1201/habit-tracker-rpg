### CHANGELOG

## [Unreleased]
- Ongoing work on additional modules (inventory, estate, economy, quests, challenges, support), tests, and docs.

## [v0.5.0-beta] - 2025-10-27

**Tasks Module - Complete Implementation**

- Implemented full CRUD API for Habits, Dailies, and Todos using DRF ViewSets.
- Added completion actions with RPG mechanics:
  - Good habits: +10 EXP, increase strength
  - Bad habits: -5 HP, decrease strength
  - Daily tasks: +15 EXP, increase strength, mark as completed
  - Todos: +20 EXP, increase strength, mark as completed
- Integrated django-filter for advanced filtering and search capabilities.
- Added filtering by type, status, strength, completion state, and custom filters (active/planned/completed).
- Implemented comprehensive test suite:
  - 15 serializer tests (validation, defaults, read-only fields)
  - 32 API/ViewSet tests (CRUD, permissions, completion logic, filtering)
  - 9 model tests (already existing)
  - Total: 56 tests for tasks module, all passing ✅
- Registered all task models in Django admin with custom list displays and filters.
- Created URL routing with RESTful endpoints:
  - `/api/tasks/habits/` - List/Create habits
  - `/api/tasks/habits/{id}/` - Retrieve/Update/Delete habit
  - `/api/tasks/habits/{id}/complete/` - Complete habit action
  - `/api/tasks/dailies/` - List/Create daily tasks
  - `/api/tasks/dailies/{id}/` - Retrieve/Update/Delete daily
  - `/api/tasks/dailies/{id}/complete/` - Complete daily action
  - `/api/tasks/todos/` - List/Create todos
  - `/api/tasks/todos/{id}/` - Retrieve/Update/Delete todo
  - `/api/tasks/todos/{id}/complete/` - Complete todo action
- Added django-filter>=24.0 to requirements.
- Ensured user isolation: users can only access their own tasks.
- Fixed serializer bugs from v0.4.0 (wrong base class, incorrect model references).

## [v0.4.0-beta] - 2025-10-24

- Implemented BaseTask abstract model and derived Habit, Daily, Todo models with inheritance.

- Added Todo.due_date validation to prevent past dates.

- Defined enums for task types, strength, status, repeat patterns, and repeat units.

- Added database indexes and constraints for improved query performance and email uniqueness.

- Refactored field naming, docstrings, and model organization in preparation for DRF integration.

## [v0.3.0-beta] - 2025-10-20
- implemented tests for user model.
- coverage for user model.
- implementing workflow for user model.

## [v0.2.0-beta] - 2025-10-15
- Added basic throttling for key authentication endpoints.
- Split user serializers into create vs read; simplified API responses.
- Adjusted profile data scope (hide email in the "me" endpoint).
- Streamlined validations for passwords and usernames.
- Moved selected settings to environment variables (deployment-friendly config).
- Improved avatar file validation.

## [v0.1.0-beta] - 2025-09-19
- Project initialization and users app setup.
- Basic JWT configuration; endpoints for registration, login, profile, and profile update.
- Initial database, static, and media settings.
