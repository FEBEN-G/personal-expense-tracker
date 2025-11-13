from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API routes - only API endpoints
    path('api/', include('api.urls')),
    
    # Frontend pages - direct template views
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('expenses/', TemplateView.as_view(template_name='expenses.html'), name='expenses'),
    path('categories/', TemplateView.as_view(template_name='categories.html'), name='categories'),
    path('analytics/', TemplateView.as_view(template_name='analytics.html'), name='analytics'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register'),
]