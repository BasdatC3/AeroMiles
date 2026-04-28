from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('staf', 'Staf'),
    ]
    TIER_CHOICES = [
        ('basic', 'Basic'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    member_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    staff_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    airline = models.ForeignKey('flights.Airline', on_delete=models.SET_NULL, null=True, blank=True, related_name='staff')

    salutation = models.CharField(max_length=10, blank=True)
    first_mid_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    country_code = models.CharField(max_length=5, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='basic')
    total_miles = models.IntegerField(default=0)
    award_miles = models.IntegerField(default=0)
    join_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.get_full_name() or self.email

    def get_full_name(self):
        name_parts = [p for p in [self.salutation, self.first_mid_name, self.last_name] if p]
        return ' '.join(name_parts) if name_parts else self.email