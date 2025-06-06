from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Movie, Genre
from datetime import timedelta, date
from django.core.files.uploadedfile import SimpleUploadedFile
import json

User = get_user_model()


class MovieTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.manager = User.objects.create_user(username='manager', password='pass', role='manager')
        self.admin = User.objects.create_user(username='admin', password='pass', role='admin')
        self.user = User.objects.create_user(username='user', password='pass', role='client')

        self.genre = Genre.objects.create(name='Action')
        self.movie = Movie.objects.create(
            title='Inception',
            country='USA',
            duration=timedelta(hours=2),
            budget=160000000,
            poster=SimpleUploadedFile("poster.jpg", b"file_content", content_type="image/jpeg"),
            description='Dream within a dream.',
            rating=8.8,
            release_date=date(2010, 7, 16)
        )
        self.movie.genre.add(self.genre)

    def test_movie_detail_view(self):
        url = reverse('movie_details', args=[self.movie.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Inception')

    def test_all_movies_access_manager(self):
        self.client.login(username='manager', password='pass')
        response = self.client.get(reverse('all_movies'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Inception')

    def test_all_movies_access_denied(self):
        self.client.login(username='user', password='pass')
        response = self.client.get(reverse('all_movies'))
        self.assertEqual(response.status_code, 403)

    def test_add_genre_valid(self):
        self.client.login(username='admin', password='pass')
        response = self.client.post(reverse('add_genre'),
                                    data=json.dumps({'name': 'Comedy'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Genre.objects.filter(name='Comedy').exists())

    def test_add_genre_empty_name(self):
        self.client.login(username='admin', password='pass')
        response = self.client.post(reverse('add_genre'),
                                    data=json.dumps({'name': ''}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_delete_movie(self):
        self.client.login(username='manager', password='pass')
        response = self.client.post(reverse('delete_movie', args=[self.movie.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Movie.objects.filter(pk=self.movie.pk).exists())

    def test_create_movie_get_form(self):
        self.client.login(username='manager', password='pass')
        response = self.client.get(reverse('movie_add'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Добавить фильм')

    def test_edit_movie_post(self):
        self.client.login(username='admin', password='pass')
        url = reverse('edit_movie', args=[self.movie.pk])

        image_content = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x01\x0A\x00\x01\x00\x2C\x00\x00\x00\x00'
            b'\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3B'
        )  # валидное GIF изображение 1x1

        data = {
            'title': 'Inception Updated',
            'country': 'USA',
            'duration': '02:00:00',
            'budget': 160000000,
            'poster': SimpleUploadedFile("poster.gif", image_content, content_type="image/gif"),
            'description': 'Updated Description.',
            'rating': 8.8,
            'release_date': '2010-07-16',
            'genre': [self.genre.pk]
        }

        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        # 🔄 Обновляем объект из базы
        self.movie.refresh_from_db()

        # ✅ Проверяем результат
        self.assertEqual(self.movie.title, 'Inception Updated')

