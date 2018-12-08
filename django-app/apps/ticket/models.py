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

    # ndc_code_unformatted = models.CharField(max_length=14, db_index=True, unique=True, default='',
    #                                         blank=True)  # Field to storing unformatted values ndc_code
    # ndc_drug_name = models.CharField(max_length=256)

    #
    # "id": 0,
    # "tickets": [
    #     "Cena bazowa: 1xNormal"
    # ],
    # "purchase_date": "2018-12-08 12:57:42",
    # "carrier": "PKP IC",
    # "start_time": "29.09 13:41",
    # "finish_time": "29.09 14:16",
    # "start_place": "Białystok",
    # "finish_place": "Mońki",
    # "class": "2",
    # "stops": [
    #     "Białystok Staros."
    # ],
    # "cost": "12.00",
    # "seats": [
    #     "14 ś"
    # ],
    # "train_number": "TLK 35100",
    # "car_number": "14",
    # "total_length": "44"
