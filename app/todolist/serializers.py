from rest_framework import serializers

from core.models import TodDoList


class ToDoListSerializer(serializers.ModelSerializer):

    class Meta:
        model = TodDoList
        fields = ['id', 'title', 'description']
        read_only_fields = ['id']


class ToDoListDetailSerializer(ToDoListSerializer):
    class Meta(ToDoListSerializer.Meta):
        fields = ToDoListSerializer.Meta.fields + ['description']
