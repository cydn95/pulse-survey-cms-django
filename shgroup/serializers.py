from rest_framework import serializers
from shgroup.models import MyMapLayout, ProjectMapLayout


class MyMapLayoutStoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyMapLayout
        fields = ['id', 'projectUser', 'project', 'layout_json']


class ProjectMapLayoutStoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectMapLayout
        fields = ['id', 'projectUser', 'project', 'layout_json']