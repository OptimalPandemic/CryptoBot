from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from crypto.serializers import UserSerializer, GroupSerializer, OrderSerializer, AssetSerializer
from crypto.models import Order, Asset


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint to view or edit Users.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [ permissions.IsAdminUser ]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint to view or edit Groups.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [ permissions.IsAdminUser ]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [ permissions.IsAdminUser ]


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [ permissions.IsAdminUser ]

