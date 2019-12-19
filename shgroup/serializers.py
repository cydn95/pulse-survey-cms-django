from rest_framework import serializers
from shgroup.models import MyMapLayoutStore


class MyMapLayoutStoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyMapLayoutStore
        fields = ['id', 'projectUser', 'project', 'layout_json']