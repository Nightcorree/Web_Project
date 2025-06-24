# atelier/views_api.py
from typing import Type, List

from django.db.models import Avg, QuerySet
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, permissions, serializers 
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.request import Request
from rest_framework.response import Response

from .models import (
    ServiceCategory, Service, PortfolioProject, BlogPost,
    Review, Order, ClientCar, OrderStatus, Role
)
from .serializers import (
    OrderCreateSerializer, OrderDetailSerializer, ServiceCategorySerializer,
    ServiceSerializer, PortfolioProjectSerializer, BlogPostSerializer,
    BlogPostDetailSerializer, UserSerializer, RegisterSerializer,
    OrderSerializer, SimpleUserSerializer, SimpleClientCarSerializer,
    SimpleOrderStatusSerializer, SimpleServiceSerializer,
    ReviewSerializer, ReviewCreateSerializer
)
from .filters import ServiceFilter
from .permissions import IsOwnerOrAdmin

# Получаем кастомную модель пользователя
User = get_user_model()


class ServiceCategoryListAPIView(generics.ListAPIView):
    """API для получения списка всех категорий услуг."""
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    pagination_class = None

class ServiceListAPIView(generics.ListAPIView):
    """API для получения списка корневых услуг (без родителя)."""
    queryset = Service.objects.filter(parent__isnull=True)
    serializer_class = ServiceSerializer

class RecentPortfolioProjectsAPIView(generics.ListAPIView):
    """API для получения нескольких последних проектов из портфолио."""
    queryset = PortfolioProject.published.select_related('base_order', 'car').all()[:3] 
    serializer_class = PortfolioProjectSerializer
    pagination_class = None

class RecentBlogPostsAPIView(generics.ListAPIView):
    """API для получения нескольких последних статей из блога."""
    queryset = BlogPost.objects.order_by('-publication_date')[:3]
    serializer_class = BlogPostSerializer
    pagination_class = None

class PortfolioProjectListAPIView(generics.ListAPIView):
    """API для получения всех опубликованных проектов портфолио."""
    queryset = PortfolioProject.published.all()
    serializer_class = PortfolioProjectSerializer
    pagination_class = None

class BlogPostListAPIView(generics.ListAPIView):
    """API для получения всех статей блога."""
    queryset = BlogPost.objects.order_by('-publication_date')
    serializer_class = BlogPostSerializer
    pagination_class = None

class BlogPostDetailAPIView(generics.RetrieveAPIView):
    """API для получения детальной информации о статье блога."""
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostDetailSerializer

class AllServicesListAPIView(generics.ListAPIView):
    """API для получения всех услуг с фильтрацией, поиском и сортировкой."""
    queryset = Service.objects.all().order_by('category__name', 'name')
    serializer_class = ServiceSerializer
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ServiceFilter
    search_fields = ['name', 'description']
    ordering_fields = ['base_price', 'name']
    
class RegisterAPIView(generics.GenericAPIView):
    """API для регистрации новых пользователей."""
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request, *args, **kwargs) -> Response:
        """Обрабатывает POST-запрос для создания нового пользователя.

        Args:
            request (Request): Объект запроса от DRF.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            Response: Ответ с данными пользователя или ошибками валидации.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) 
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "Пользователь успешно зарегистрирован."
        }, status=status.HTTP_201_CREATED)

class UserMeView(generics.RetrieveAPIView):
    """API для получения данных о текущем аутентифицированном пользователе."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self) -> User: # type: ignore
        """Возвращает объект текущего пользователя.

        Returns:
            User: Объект `User` из запроса.
        """
        return self.request.user
    
class OrderListAPIView(generics.ListAPIView):
    """API для получения списка заказов с учетом роли пользователя."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet[Order]:
        """Возвращает список заказов в зависимости от роли текущего пользователя.

        Returns:
            QuerySet[Order]: Отфильтрованный и оптимизированный queryset заказов.
        """
        user: User = self.request.user # type: ignore
        
        queryset = Order.objects.select_related('client', 'car', 'status').prefetch_related('performers')

        if user.roles.filter(name='Администратор').exists():
            return queryset.all()
        
        elif user.roles.filter(name='Автомеханик').exists():
            return queryset.filter(performers=user)
            
        elif user.roles.filter(name='Клиент').exists():
            return queryset.filter(client=user)
            
        return Order.objects.none()
    
class OrderCreateAPIView(generics.CreateAPIView):
    """API для создания новых заказов (только для админов)."""
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAdminUser]

class ClientListAPIView(generics.ListAPIView):
    """API для получения списка пользователей с ролью 'Клиент'."""
    queryset = User.objects.filter(roles__name='Клиент').order_by('full_name')
    serializer_class = SimpleUserSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = None

class CarListAPIView(generics.ListAPIView):
    """API для получения списка всех автомобилей клиентов."""
    queryset = ClientCar.objects.select_related('owner').all()
    serializer_class = SimpleClientCarSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = None

class StatusListAPIView(generics.ListAPIView):
    """API для получения списка всех статусов заказов."""
    queryset = OrderStatus.objects.all()
    serializer_class = SimpleOrderStatusSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = None

class PerformerListAPIView(generics.ListAPIView):
    """API для получения списка всех исполнителей (сотрудников)."""
    queryset = User.objects.filter(is_staff=True).order_by('full_name')
    serializer_class = SimpleUserSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = None
    
class ServiceListForOrderAPIView(generics.ListAPIView):
    """API для получения списка всех услуг для использования в формах."""
    queryset = Service.objects.all().order_by('name')
    serializer_class = SimpleServiceSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = None
    
class OrderDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API для просмотра, обновления и удаления одного конкретного заказа."""
    queryset = Order.objects.select_related('client', 'car', 'status').prefetch_related('performers', 'order_items__service').all()
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self) -> Type[serializers.ModelSerializer]:
        """Возвращает класс сериализатора в зависимости от метода запроса.

        Для `GET` используется детальный `OrderDetailSerializer`.
        Для `PUT`/`PATCH` используется `OrderCreateSerializer`.

        Returns:
            Type[serializers.ModelSerializer]: Класс нужного сериализатора.
        """
        if self.request.method in ['PUT', 'PATCH']:
            return OrderCreateSerializer
        return OrderDetailSerializer
    
class ReviewListCreateAPIView(generics.ListCreateAPIView):
    """API для получения списка отзывов и создания нового."""
    queryset = Review.objects.select_related('user', 'order').prefetch_related('order__order_items__service').all()
    
    def get_serializer_class(self) -> Type[serializers.ModelSerializer]:
        """Возвращает сериализатор в зависимости от метода: `ReviewCreateSerializer`
        для POST и `ReviewSerializer` для GET."""
        if self.request.method == 'POST':
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_permissions(self) -> List[permissions.BasePermission]:
        """Устанавливает права доступа в зависимости от метода.
        
        - Для создания (POST) требуется аутентификация.
        - Для просмотра списка (GET) доступ разрешен всем.
        """
        if self.request.method == 'POST':
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    def list(self, request: Request, *args, **kwargs) -> Response:
        """Переопределяет стандартный метод `list` для добавления среднего рейтинга.

        Args:
            request (Request): Объект запроса от DRF.
            *args: Позиционные аргументы.
            **kwargs: Именованные аргументы.

        Returns:
            Response: Кастомный ответ, содержащий `average_rating` и `reviews`.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        avg_rating = Review.objects.all().aggregate(Avg('rating'))['rating__avg'] or 0
        
        data = {
            'average_rating': round(avg_rating, 2),
            'reviews': serializer.data
        }
        return Response(data)

class ReviewDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API для просмотра, обновления и удаления конкретного отзыва."""
    queryset = Review.objects.all()
    serializer_class = ReviewCreateSerializer
    permission_classes = [IsOwnerOrAdmin]

class UserOrderListAPIView(generics.ListAPIView):
    """Возвращает список заказов текущего пользователя, на которые можно оставить отзыв."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    
    def get_queryset(self) -> QuerySet[Order]:
        """Возвращает заказы текущего пользователя со статусом "Завершен",
        на которые еще не был оставлен отзыв."""
        user: User = self.request.user # type: ignore
        reviewed_orders_ids = Review.objects.filter(user=user).values_list('order_id', flat=True)
        
        return Order.objects.filter(
            client=user, 
            status__name="Завершен" 
        ).exclude(id__in=reviewed_orders_ids)