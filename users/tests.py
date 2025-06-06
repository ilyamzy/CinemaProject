from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

User = get_user_model()

class UserTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = 'TestPassword123!'
        self.admin = User.objects.create_user(
            username='adminuser', email='admin@example.com', phone_number='1234567890',
            first_name='Admin', last_name='User', password=self.password, role='admin'
        )
        self.manager = User.objects.create_user(
            username='manageruser', email='manager@example.com', phone_number='1234567891',
            first_name='Manager', last_name='User', password=self.password, role='manager'
        )
        self.user = User.objects.create_user(
            username='normaluser', email='user@example.com', phone_number='1234567892',
            first_name='Normal', last_name='User', password=self.password, role='user'
        )

    def test_register_user(self):
        url = reverse('users:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'phone_number': '5555555555',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('users:login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_user_duplicate_email(self):
        url = reverse('users:register')
        data = {
            'username': 'newuser2',
            'email': 'user@example.com',  # duplicate email
            'phone_number': '5555555556',
            'first_name': 'New',
            'last_name': 'User2',
            'password1': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
        }
        response = self.client.post(url, data)
        self.assertContains(response, 'Такой E-mail уже существует!')

    def test_login_user(self):
        url = reverse('users:login')
        response = self.client.post(url, {
            'username': self.user.username,
            'password': self.password
        })
        self.assertRedirects(response, reverse('home'))

    def test_profile_user_access(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('users:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)

    def test_profile_user_update(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('users:profile')
        new_first_name = 'UpdatedName'
        response = self.client.post(url, {
            'username': self.user.username,
            'email': self.user.email,
            'phone_number': '9999999999',
            'first_name': new_first_name,
            'last_name': self.user.last_name,
        })
        self.assertRedirects(response, reverse('users:profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, new_first_name)

    def test_add_manager_admin_only(self):
        self.client.login(username=self.admin.username, password=self.password)
        url = reverse('users:add_manager')
        response = self.client.post(url, {'username': self.user.username})
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'manager')
        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('успешно изменена на "manager"' in str(m) for m in messages))

    def test_add_manager_denied_for_non_admin(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('users:add_manager')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_add_manager_invalid_user(self):
        self.client.login(username=self.admin.username, password=self.password)
        url = reverse('users:add_manager')
        response = self.client.post(url, {'username': 'nonexistent'})
        self.assertContains(response, 'Пользователь не найден.')

    def test_add_manager_already_manager(self):
        self.client.login(username=self.admin.username, password=self.password)
        url = reverse('users:add_manager')
        response = self.client.post(url, {'username': self.manager.username})
        self.assertContains(response, f'Вы не можете изменить роль пользователя {self.manager.username}')

    def test_logout(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(reverse('users:logout'))
        self.assertRedirects(response, '/')
