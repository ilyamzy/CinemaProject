import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Hall, Seat


User = get_user_model()


class HallViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.manager = User.objects.create_user(
            username='manager', password='testpass123', role='manager'
        )
        self.admin = User.objects.create_user(
            username='admin', password='testpass123', role='admin'
        )
        self.user = User.objects.create_user(
            username='user', password='testpass123', role='user'
        )

    def test_hall_create_view_permission(self):
        # Not logged in
        response = self.client.get(reverse('hall_create'))
        self.assertEqual(response.status_code, 302)  # redirected to login

        # Logged in as user (no permission)
        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('hall_create'))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        # Logged in as manager (has permission)
        self.client.login(username='manager', password='testpass123')
        response = self.client.get(reverse('hall_create'))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_hall_save_view_permission(self):
        url = reverse('hall_save')
        data = {
            'name': 'Test Hall',
            'rows': '3',
            'cols': '4',
            'seats': json.dumps([
                {"row": 1, "col": 1, "type": "single"},
                {"row": 1, "col": 2, "type": "double"},
                {"row": 2, "col": 1, "type": "single"}
            ])
        }

        # Not logged in
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # redirected to login

        # Logged in as user (no permission)
        self.client.login(username='user', password='testpass123')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        # Logged in as manager (has permission)
        self.client.login(username='manager', password='testpass123')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.json())
        hall_id = response.json()['id']
        self.assertTrue(Hall.objects.filter(id=hall_id).exists())
        self.assertEqual(Seat.objects.filter(hall_id=hall_id).count(), 3)
        self.client.logout()

    def test_hall_save_invalid_json(self):
        self.client.login(username='admin', password='testpass123')
        url = reverse('hall_save')
        data = {
            'name': 'Bad Hall',
            'rows': '2',
            'cols': '4',
            'seats': 'not a json'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('seats', response.json()['errors'])
        self.client.logout()

    def test_hall_save_invalid_seat_type(self):
        self.client.login(username='admin', password='testpass123')
        url = reverse('hall_save')
        data = {
            'name': 'Bad Hall',
            'rows': '2',
            'cols': '4',
            'seats': json.dumps([
                {"row": 1, "col": 1, "type": "triple"},  # invalid type
            ])
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Ошибка в описании места', str(response.json()['errors']))
        self.client.logout()

    def test_all_halls_view(self):
        Hall.objects.create(name="Hall 1", rows=2, cols=2)
        Hall.objects.create(name="Hall 2", rows=3, cols=5)
        response = self.client.get(reverse('all_halls'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hall 1")
        self.assertContains(response, "Hall 2")

    def test_delete_hall_permission(self):
        hall = Hall.objects.create(name="Delete Me", rows=2, cols=2)
        url = reverse('delete_hall', args=[hall.id])

        # Not logged in
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        # Logged in as user
        self.client.login(username='user', password='testpass123')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        # Logged in as manager
        self.client.login(username='manager', password='testpass123')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Hall.objects.filter(id=hall.id).exists())
        self.client.logout()

    def test_delete_nonexistent_hall(self):
        self.client.login(username='admin', password='testpass123')
        url = reverse('delete_hall', args=[9999])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Movie not found', response.json()['error'])
        self.client.logout()
