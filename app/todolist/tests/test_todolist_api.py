from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import TodDoList

from todolist.serializers import ToDoListSerializer, ToDoListDetailSerializer

TODOLIST_URL = reverse("todolist:todolist-list")


def detail_url(todolist_id):
    return reverse('todolist:todolist-detail', args=[todolist_id])


def create_todolist(user, **params):
    defaults = {
        'title': 'Sample todo list title',
        'description': 'Sample description for sample todo list'
    }

    defaults.update(params)

    todolist = TodDoList.objects.create(user=user, **defaults)
    return todolist


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicToDoListAPITests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TODOLIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateToDoListAPITests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user(email='user@example.com',
                                password='testpass123')
        self.client.force_authenticate(self.user)

    def test_retrieve_todolist(self):

        create_todolist(user=self.user)
        create_todolist(user=self.user)

        res = self.client.get(TODOLIST_URL)

        todolists = TodDoList.objects.all().order_by('-id')

        serializer = ToDoListSerializer(todolists, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_todolist_list_limited_to_user(self):
        new_user = create_user(email='newuser@example.com',
                               password='testpass123')

        create_todolist(user=new_user)
        create_todolist(user=self.user)

        res = self.client.get(TODOLIST_URL)

        todolists = TodDoList.objects.filter(user=self.user)
        serializer = ToDoListSerializer(todolists, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_todolist_detail(self):
        todolist = create_todolist(user=self.user)

        url = detail_url(todolist.id)
        res = self.client.get(url)

        serializer = ToDoListDetailSerializer(todolist)
        self.assertEqual(res.data, serializer.data)

    def test_create_todolist(self):
        payload = {
            'title': 'Sample list',
            'description': 'Simple description of the list'
        }
        res = self.client.post(TODOLIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        todolist = TodDoList.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(todolist, k), v)
        self.assertEqual(todolist.user, self.user)

    def test_partial_update(self):
        original_description = "Original list description"
        todolist = TodDoList.objects.create(
            title='Sample list title',
            description=original_description,
            user=self.user
        )
        payload = {'title': 'New List title'}

        url = detail_url(todolist.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        todolist.refresh_from_db()
        self.assertEqual(todolist.title, payload['title'])
        self.assertEqual(todolist.description, original_description)
        self.assertEqual(todolist.user, self.user)

    def test_full_update(self):
        todolist = TodDoList.objects.create(
            title='This is the list title',
            description='This is the description of the list',
            user=self.user
        )

        payload = {
            'title': 'This is the updated list title',
            'description': 'Some modifications to list description'
        }

        url = detail_url(todolist.id)
        res = self.client.put(url, payload)
        todolist.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for k, v in payload.items():
            self.assertEqual(getattr(todolist, k), v)
        self.assertEqual(todolist.user, self.user)

    def test_update_user_return_error(self):
        new_user = create_user(email="newuser2@exaqmple.com",
                               password="1234test")
        todolist = create_todolist(user=self.user)
        payload = {'user': new_user.id}
        url = detail_url(todolist.id)
        res = self.client.patch(url, payload)
        todolist.refresh_from_db()
        self.assertEqual(todolist.user, self.user)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_todolist(self):
        todolist = create_todolist(user=self.user)
        url = detail_url(todolist.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TodDoList.objects.filter(id=todolist.id).exists())

    def test_delete_other_users_todolist_error(self):
        new_user = create_user(email="user3@example.com", password="123123")
        todolist = create_todolist(user=new_user)

        url = detail_url(todolist.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(TodDoList.objects.filter(id=todolist.id).exists())
