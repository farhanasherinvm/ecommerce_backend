from django.urls import path, include
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LogoutView, CategoryViewSet, ProductViewSet, CartViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('products', ProductViewSet, basename='product')
router.register('cart', CartViewSet, basename='cart')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('', include(router.urls)),
]
