from django.db import models


class Movie(models.Model):
    title = models.CharField("Название", max_length=200)
    country = models.CharField("Страна", max_length=100)
    genre = models.ManyToManyField('Genre', verbose_name="Жанр")
    duration = models.DurationField("Длительность")
    budget = models.DecimalField("Бюджет", max_digits=20, decimal_places=2)
    poster = models.ImageField("Постер", upload_to='posters/')
    description = models.TextField("Описание")
    rating = models.FloatField("Рейтинг")
    release_date = models.DateField("Дата выхода")

    def __str__(self):
        return self.title

class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
