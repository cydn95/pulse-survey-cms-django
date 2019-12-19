from rest_framework import serializers
from shgroup.models import MyMapLayoutStore, ProjectMapLayoutStore


class MyMapLayoutStoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyMapLayoutStore
        fields = ['id', 'projectUser', 'project', 'layout_json']


class ProjectMapLayoutStoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectMapLayoutStore
        fields = ['id', 'projectUser', 'project', 'layout_json']