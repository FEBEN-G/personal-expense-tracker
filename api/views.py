from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout, authenticate
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from django.db import IntegrityError
import json
from .models import Category, Expense
from .serializers import (
    UserRegistrationSerializer, UserSerializer, CategorySerializer,
    ExpenseSerializer, ExpenseSummarySerializer
)
from .permissions import IsOwner, IsCategoryOwner

# ==================== CLEAN AUTHENTICATION SYSTEM ====================

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def register_view(request):
    """
    Clean user registration endpoint - FIXED VERSION
    """
    print("🎯 REGISTER ENDPOINT HIT!")  # Debug line
    
    try:
        # FIXED: Use request.data instead of json.loads(request.body)
        # DRF automatically parses JSON and form data into request.data
        data = request.data
        print(f"📊 Request data: {data}")  # Debug line
        print(f"📦 Content-Type: {request.content_type}")  # Debug line
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        password2 = data.get('password2', '')
        
        print(f"👤 Registration attempt: {username}")  # Debug line
        
        # Validation
        if not username or not email or not password:
            print("❌ Missing fields")  # Debug line
            return Response({
                'success': False,
                'error': 'All fields are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(username) < 3:
            print("❌ Username too short")  # Debug line
            return Response({
                'success': False,
                'error': 'Username must be at least 3 characters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(password) < 8:
            print("❌ Password too short")  # Debug line
            return Response({
                'success': False,
                'error': 'Password must be at least 8 characters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if password != password2:
            print("❌ Passwords don't match")  # Debug line
            return Response({
                'success': False,
                'error': 'Passwords do not match'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print("❌ Username exists")  # Debug line
            return Response({
                'success': False,
                'error': 'Username already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            print("❌ Email exists")  # Debug line
            return Response({
                'success': False,
                'error': 'Email already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Create auth token
            token, created = Token.objects.get_or_create(user=user)
            
            # Log the user in
            login(request, user)
            
            print(f"✅ User registered successfully: {username}")  # Debug line
            
            return Response({
                'success': True,
                'message': 'Registration successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                },
                'token': token.key
            }, status=status.HTTP_201_CREATED)
            
        except IntegrityError as e:
            print(f"❌ Integrity error: {e}")  # Debug line
            return Response({
                'success': False,
                'error': 'User creation failed'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")  # Debug line
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")  # Debug line
        return Response({
            'success': False,
            'error': 'Internal server error: ' + str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def login_view(request):
    """
    Clean login endpoint with session and token authentication - FIXED VERSION
    """
    print("🎯 LOGIN ENDPOINT HIT!")  # Debug line
    
    try:
        # FIXED: Use request.data instead of json.loads(request.body)
        data = request.data
        print(f"📊 Request data: {data}")  # Debug line
        print(f"📦 Content-Type: {request.content_type}")  # Debug line
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        print(f"👤 Login attempt: {username}")  # Debug line
        
        # Basic validation
        if not username or not password:
            print("❌ Missing username or password")  # Debug line
            return Response({
                'success': False,
                'error': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                # Login user (creates session)
                login(request, user)
                
                # Get or create token
                token, created = Token.objects.get_or_create(user=user)
                
                print(f"✅ Login successful: {user.username}")  # Debug line
                
                return Response({
                    'success': True,
                    'message': 'Login successful',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                    },
                    'token': token.key
                }, status=status.HTTP_200_OK)
            else:
                print("❌ Account disabled")  # Debug line
                return Response({
                    'success': False,
                    'error': 'Account is disabled'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            print(f"❌ Login failed for user: {username}")  # Debug line
            return Response({
                'success': False,
                'error': 'Invalid username or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")  # Debug line
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")  # Debug line
        return Response({
            'success': False,
            'error': 'Internal server error: ' + str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Clean logout endpoint
    """
    try:
        # Delete the user's token
        try:
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass  # Token doesn't exist, that's fine
        
        # Logout user (destroys session)
        logout(request)
        
        return Response({
            'success': True,
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def get_csrf_token(request):
    """
    Get CSRF token for forms
    """
    return Response({
        'success': True,
        'csrfToken': get_token(request)
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_auth(request):
    """
    Check if user is authenticated
    """
    return Response({
        'success': True,
        'authenticated': True,
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email
        }
    })

# ==================== TEMPLATE VIEWS ====================

class HomePageView(TemplateView):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        # Only redirect to dashboard if user is authenticated AND trying to access home
        if request.user.is_authenticated and request.path == '/':
            return redirect('/dashboard/')
        return super().get(request, *args, **kwargs)

class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get(self, request, *args, **kwargs):
        # Only redirect to login if user is NOT authenticated
        if not request.user.is_authenticated:
            return redirect('/login/')
        return super().get(request, *args, **kwargs)

class LoginPageView(TemplateView):
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        # If user is already authenticated, redirect to dashboard
        if request.user.is_authenticated:
            return redirect('/dashboard/')
        return super().get(request, *args, **kwargs)

class RegisterPageView(TemplateView):
    template_name = 'register.html'

    def get(self, request, *args, **kwargs):
        # If user is already authenticated, redirect to dashboard
        if request.user.is_authenticated:
            return redirect('/dashboard/')
        return super().get(request, *args, **kwargs)

# ==================== API VIEWSETS ====================

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
        
        return queryset.order_by('-date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get total expense summary"""
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
        
        category_breakdown = Category.objects.filter(
            user=request.user
        ).annotate(
            total_amount=Sum('expenses__amount')
        ).values('id', 'name', 'total_amount')
        
        serializer = ExpenseSummarySerializer({
            'total_expenses': summary_data['total_expenses'] or 0,
            'total_count': summary_data['total_count'] or 0,
            'average_expense': summary_data['average_expense'] or 0,
            'currency': 'USD',
            'start_date': start_date,
            'end_date': end_date,
            'category_breakdown': list(category_breakdown)
        })
        
        return Response(serializer.data)