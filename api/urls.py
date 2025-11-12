from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView  # Make sure this import exists
from .views import (
    CategoryViewSet, 
    ExpenseViewSet, 
    HomePageView, 
    DashboardView,
    LoginPageView,
    RegisterPageView,
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
    # API routes
    path('api/', include(router.urls)),
    path('api/auth/register/', register_view, name='register'),
    path('api/auth/login/', login_view, name='login'),
    path('api/auth/logout/', logout_view, name='logout'),
    path('api/auth/csrf/', get_csrf_token, name='csrf_token'),
    path('api/auth/check/', check_auth, name='check_auth'),
    
    # HTML pages - Use simple TemplateView without redirect logic
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('home/', TemplateView.as_view(template_name='home.html'), name='home'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login_page'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register_page'),
    path('expenses/', TemplateView.as_view(template_name='expenses.html'), name='expenses'),
    path('categories/', TemplateView.as_view(template_name='categories.html'), name='categories'),
    path('analytics/', TemplateView.as_view(template_name='analytics.html'), name='analytics'),
    path('profile/', TemplateView.as_view(template_name='profile.html'), name='profile'),
]