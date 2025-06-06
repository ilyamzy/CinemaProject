from datetime import timezone
from django.db import models


from movies.models import Movie
from halls.models import Hall


class CinemaSession(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='sessions')
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='sessions')
    start_time = models.DateTimeField()
    single_seat_price = models.DecimalField(max_digits=6, decimal_places=2, default=16)
    double_seat_price = models.DecimalField(max_digits=6, decimal_places=2, default=32)

    def end_time(self):
        return self.start_time + self.movie.duration

