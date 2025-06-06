from django.db import models


class Hall(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(
        "Иконка",
        upload_to='hall_icons/',
        default='hall_icons/default_hall_icon.png'
    )
    rows = models.PositiveIntegerField()
    cols = models.PositiveIntegerField()


class Seat(models.Model):
    SEAT_TYPES = (
        ('single', 'Single'),
        ('double', 'Double'),
    )
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='seats')
    row = models.PositiveIntegerField()
    col = models.PositiveIntegerField()
    seat_type = models.CharField(max_length=10, choices=SEAT_TYPES)

    class Meta:
        unique_together = ('hall', 'row', 'col')
