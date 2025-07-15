from rest_framework import serializers
from .models import Hero

class HeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hero
        fields = ['api_id', 'name', 'intelligence', 'strength', 'speed', 'power']

    def create(self, validated_data):
        return Hero.objects.create(**validated_data)