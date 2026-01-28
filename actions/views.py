from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Category, ActionTemplate, Action
from .serializers import CategorySerializer, ActionTemplateSerializer, ActionSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Category viewset (read-only)"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class ActionTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """Action template viewset (read-only)"""
    queryset = ActionTemplate.objects.filter(is_active=True)
    serializer_class = ActionTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['category']
    ordering_fields = ['name', 'xp_reward']


class ActionViewSet(viewsets.ModelViewSet):
    """Action viewset for CRUD"""
    serializer_class = ActionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['category', 'user']
    ordering_fields = ['-created_at', 'xp_earned']

    def get_queryset(self):
        """Return actions for current user"""
        user = self.request.user
        return Action.objects.filter(user=user).order_by('-created_at')

    def perform_create(self, serializer):
        """Create action with current user"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_actions(self, request):
        """Get current user's actions"""
        actions = self.get_queryset()
        serializer = self.get_serializer(actions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def today(self, request):
        """Get today's actions for current user"""
        from django.utils import timezone
        today = timezone.now().date()
        actions = self.get_queryset().filter(created_at__date=today)
        serializer = self.get_serializer(actions, many=True)
        return Response(serializer.data)