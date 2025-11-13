from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, 
    ExpenseViewSet, 
    register_view,
    login_view, 
    logout_view, 
    get_csrf_token,
    check_auth
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'expenses', ExpenseViewSet, basename='expense')

urlpatterns = [
    # API endpoints under /api/
    path('', include(router.urls)),
    path('auth/register/', register_view, name='register'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/csrf/', get_csrf_token, name='csrf_token'),
    path('auth/check/', check_auth, name='check_auth'),
    
    # Remove all HTML page routes from here - they belong in main urls.py
]