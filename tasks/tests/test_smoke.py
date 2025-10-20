def test_import_tasks_modules():
    # Ensure tasks app modules import without errors to contribute minimal coverage
    __import__("tasks.models")
    __import__("tasks.views")
