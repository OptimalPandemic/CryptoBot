from django.db import models

# Create your models here.
class Order(models.Model):
    ORDER_STATUSES = [
        ('o', 'open'),
        ('c', 'closed'),
        ('a', 'cancelled'),
        ('e', 'expired'),
    ]
    ORDER_TYPES = [
        ('m', 'market'),
        ('l', 'limit'),
    ]
    ORDER_SIDES = [
        ('b', 'buy'),
        ('s', 'sell'),
    ]
    symbol = models.CharField(max_length=10)
    timestamp = models.IntegerField()
    status = models.CharField(max_length=1, choices=ORDER_STATUSES)
    type = models.CharField(max_length=1, choices=ORDER_TYPES)
    side = models.CharField(max_length=1, choices=ORDER_SIDES)
    cost = models.DecimalField(max_digits=10, decimal_places=10)
    amount = models.DecimalField(max_digits=10, decimal_places=10)
    filled = models.DecimalField(max_digits=10, decimal_places=10)
    remaining = models.DecimalField(max_digits=10, decimal_places=10)
    fee_currency = models.CharField(max_length=4)
    fee = models.DecimalField(max_digits=10, decimal_places=10)
    fee_rate = models.DecimalField(max_digits=10, decimal_places=10)

    class Meta:
        ordering = ['timestamp']

class Asset(models.Model):
    currency = models.CharField(max_length=4)
    free = models.DecimalField(max_digits=10, decimal_places=10)
    used = models.DecimalField(max_digits=10, decimal_places=10)
    total = models.DecimalField(max_digits=10, decimal_places=10)