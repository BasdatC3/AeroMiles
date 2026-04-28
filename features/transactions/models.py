from django.db import models


class ClaimMiles(models.Model):
    CLAIM_TYPE_CHOICES = [
        ('missing', 'Missing Miles'),
        ('bonus', 'Bonus Miles'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='claims')
    flight = models.ForeignKey('flights.Flight', on_delete=models.SET_NULL, null=True, blank=True)
    claim_type = models.CharField(max_length=20, choices=CLAIM_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    miles = models.IntegerField()
    description = models.TextField(blank=True)
    approved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_claims')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.claim_type} - {self.miles} miles"


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('earn', 'Earn'),
        ('spend', 'Spend'),
        ('bonus', 'Bonus'),
        ('expire', 'Expire'),
        ('transfer', 'Transfer'),
    ]

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    miles = models.IntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.type} - {self.miles}"


class TransferMiles(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    sender = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='sent_transfers')
    recipient = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='received_transfers')
    miles = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.sender} -> {self.recipient}"