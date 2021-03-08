from django.contrib.auth.models import User, Group
from rest_framework import serializers
from crypto.models import Order, Asset

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class OrderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Order
        fields = ['url', 'id', 'symbol', 'timestamp', 'status', 'type', 'side', 'cost', 'amount',
        'filled', 'remaining', 'fee_currency', 'fee', 'fee_rate']

class AssetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Asset
        fields = ['url', 'currency', 'free', 'used', 'total']