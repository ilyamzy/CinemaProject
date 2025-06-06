from django.db import models


from cinema_sessions.models import CinemaSession
from halls.models import Seat
from users.models import CustomUser


class Ticket(models.Model):
    session = models.ForeignKey(CinemaSession, on_delete=models.CASCADE, related_name='tickets')
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='tickets')
    is_reserved = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)

    class Meta:
        unique_together = ('session', 'seat')
