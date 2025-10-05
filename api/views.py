from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import login, logout
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import datetime
from .models import Category, Expense
from .serializers import (
    UserRegistrationSerializer, UserSerializer, CategorySerializer,
    ExpenseSerializer, ExpenseSummarySerializer
)
from .permissions import IsOwner, IsCategoryOwner

class UserRegistrationViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create token for the new user
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user, context=self.get_serializer_context()).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email
        })

class LogoutViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        try:
            # Delete the token to logout
            request.user.auth_token.delete()
        except:
            pass
        
        logout(request)
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsCategoryOwner]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        queryset = Expense.objects.filter(user=self.request.user)
        
        # Filter by category if provided
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                pass
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def by_category(self, request, pk=None):
        """Get expenses by specific category ID"""
        try:
            category = Category.objects.get(id=pk, user=request.user)
        except Category.DoesNotExist:
            return Response(
                {"detail": "Category not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        expenses = Expense.objects.filter(user=request.user, category=category)
        serializer = self.get_serializer(expenses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get total expense summary, optionally filtered by date range"""
        queryset = Expense.objects.filter(user=request.user)
        
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                pass
        
        summary_data = queryset.aggregate(
            total_expenses=Sum('amount'),
            total_count=Count('id'),
            average_expense=Avg('amount')
        )
        
        serializer = ExpenseSummarySerializer({
            'total_expenses': summary_data['total_expenses'] or 0,
            'total_count': summary_data['total_count'] or 0,
            'average_expense': summary_data['average_expense'] or 0,
            'currency': 'USD',
            'start_date': start_date,
            'end_date': end_date
        })
        
        return Response(serializer.data)