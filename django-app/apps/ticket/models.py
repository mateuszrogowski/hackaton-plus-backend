from django.contrib.postgres.fields import ArrayField
from django.db import models


class Ticket(models.Model):
    tickets = ArrayField(
        models.CharField(max_length=128),
        blank=True,
        null=True,
        default=list
    )
    purchase_date = models.DateTimeField()
    carrier = models.CharField(max_length=128, blank=True, default='')
    start_time = models.DateTimeField()
    finish_time = models.DateTimeField()
    start_place = models.CharField(max_length=128, default='', blank=True)
    finish_place = models.CharField(max_length=128, default='', blank=True)
    car_class = models.IntegerField(blank=True, default=2)
    stops = ArrayField(
        models.CharField(max_length=128),
        blank=True,
        null=True,
        default=list
    )
    cost = models.DecimalField(decimal_places=2, max_digits=10, blank=True, default=None, null=True)
    seats = ArrayField(
        models.CharField(max_length=128),
        blank=True,
        null=True,
        default=list
    )
    train_number = models.CharField(max_length=128, default='', blank=True)
    car_number = models.IntegerField(null=True, default=None, blank=True)
    total_length = models.IntegerField(null=True, default=None, blank=True)
    qr_code = models.TextField(verbose_name="QR Code", null=True, default=None, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
