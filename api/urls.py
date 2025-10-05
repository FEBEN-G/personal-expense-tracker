from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationViewSet, CustomAuthToken, LogoutViewSet,
    CategoryViewSet, ExpenseViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'expenses', ExpenseViewSet, basename='expense')

auth_patterns = [
    path('register/', UserRegistrationViewSet.as_view({'post': 'create'}), name='register'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('logout/', LogoutViewSet.as_view({'post': 'create'}), name='logout'),
]

urlpatterns = [
    path('auth/', include(auth_patterns)),
    path('', include(router.urls)),
]