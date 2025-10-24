### CHANGELOG

## [Unreleased]
- Ongoing work on additional modules (economy, challenges), tests, and docs.

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
