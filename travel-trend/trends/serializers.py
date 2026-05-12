from rest_framework import serializers


class TrendItemSerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    keyword = serializers.CharField()
    category = serializers.CharField()
    life_cycle = serializers.CharField()
    context = serializers.CharField()
    rising_percentage = serializers.IntegerField()


class RouteItemSerializer(serializers.Serializer):
    time = serializers.CharField()
    keyword = serializers.CharField()
    place = serializers.CharField()
    description = serializers.CharField()
