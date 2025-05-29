from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Category, Product, Cart
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .serializers import (
    RegisterSerializer,
    CategorySerializer,
    ProductSerializer,
    CartSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken

# --- Authentication Views ---

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = []


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token or token already blacklisted."}, status=status.HTTP_400_BAD_REQUEST)


# --- Category Views ---

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method in ['POST']:
            return [IsAdminUser()]
        return []


# --- Product Views ---

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category']  # 🔍 Filter by category
    search_fields = ['name']         # 🔍 Search by product name
    def get_permissions(self):
        if self.request.method in ['POST', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return []

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({"products": serializer.data})
        serializer = self.get_serializer(queryset, many=True)
        return Response({"products": serializer.data})

    def retrieve(self, request, pk=None):
        try:
            product = self.get_object()
            serializer = self.get_serializer(product)
            return Response({"product": serializer.data})
        except:
            return Response({"error": "Product not found"}, status=404)


# --- Cart Views ---

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"cart": serializer.data})

    def partial_update(self, request, pk=None):
        cart_item = self.get_object()
        serializer = self.get_serializer(cart_item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"cart_item": serializer.data})

    def destroy(self, request, pk=None):
        cart_item = self.get_object()
        cart_item.delete()
        return Response({"detail": "Cart item deleted successfully."})
