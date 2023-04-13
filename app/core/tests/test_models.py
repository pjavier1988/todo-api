
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


class ModelTests(TestCase):

    def test_when_create_user_with_email_expects_successfull(self):

        email = 'prueba@ejemplo.com'
        password = 'pass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_validated(self):
        sample_emails = [
            ['email1@EXAMPLE.com', 'email1@example.com'],
            ['Email2@Example.com', 'Email2@example.com']
        ]
        for email, expected_email in sample_emails:
            user = get_user_model().objects.create_user(email, '123')
            self.assertEqual(user.email, expected_email)

    def test_when_user_is_created_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', '123')

    def test_when_create_superuser_is_true(self):
        user = get_user_model().objects.create_superuser(
            'test1@example.com',
            '123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_todolist(self):
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )
        todolist = models.TodDoList.objects.create(
            user=user,
            title='Sample list name',
            description='Sample list description',
        )

        self.assertEqual(str(todolist), todolist.title)
