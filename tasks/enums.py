from django.db import models


class HabitType(models.TextChoices):
    GOOD = 'good', 'Good'
    BAD = 'bad', 'Bad'
    
    
class TasksStrength(models.TextChoices):
    FRAGILE = 'fragile', 'Fragile'
    WEAK = 'weak', 'Weak'
    STABLE = 'stable', 'Stable'
    STRONG = 'strong', 'Strong'
    UNBREAKABLE = 'unbreakable', 'Unbreakable'
    

class TasksStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    COMPLETED = 'completed', 'Completed'
    
class TasksRepeats(models.TextChoices):
    DAILY = 'daily', 'Daily'
    WEEKLY = 'weekly', 'Weekly'
    MONTHLY = 'monthly', 'Monthly'
    YEARLY = 'yearly', 'Yearly'
    
    
class TasksRepeatOn(models.TextChoices):
    MONDAY = 'monday', 'Monday'
    TUESDAY = 'tuesday', 'Tuesday'
    WEDNESDAY = 'wednesday', 'Wednesday'
    THURSDAY = 'thursday', 'Thursday'
    FRIDAY = 'friday', 'Friday'
    SATURDAY = 'saturday', 'Saturday'
    SUNDAY = 'sunday', 'Sunday'
    EVERYDAY = 'everyday', 'Everyday'
    
class RepeatUnit(models.TextChoices):
    DAYS = 'days', 'Days'
    WEEKS = 'weeks', 'Weeks'
    MONTHS = 'months', 'Months'