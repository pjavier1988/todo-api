from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from todolist.views import ToDoListViewSet


router = DefaultRouter()
router.register('todolists', ToDoListViewSet, basename='todolist')

app_name = 'todolist'

urlpatterns = [
     path('', include(router.urls)),
]
