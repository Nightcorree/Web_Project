# atelier/views_api.py
from rest_framework import generics, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg

from .models import (
    ServiceCategory, Service, PortfolioProject, BlogPost,
    Review, Order, User, ClientCar, OrderStatus, Role
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


class ServiceCategoryListAPIView(generics.ListAPIView):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    pagination_class = None

class ServiceListAPIView(generics.ListAPIView):
    queryset = Service.objects.filter(parent__isnull=True)
    serializer_class = ServiceSerializer


class RecentPortfolioProjectsAPIView(generics.ListAPIView):
    # Используем наш кастомный менеджер для получения опубликованных проектов
    queryset = PortfolioProject.published.select_related('base_order', 'car').all()[:3] 
    serializer_class = PortfolioProjectSerializer
    pagination_class = None

class RecentBlogPostsAPIView(generics.ListAPIView):
    # Берем 3 последние статьи
    queryset = BlogPost.objects.order_by('-publication_date')[:3]
    serializer_class = BlogPostSerializer
    pagination_class = None

class PortfolioProjectListAPIView(generics.ListAPIView):
    # Используем наш кастомный менеджер для получения всех опубликованных проектов
    queryset = PortfolioProject.published.all()
    serializer_class = PortfolioProjectSerializer
    pagination_class = None

class BlogPostListAPIView(generics.ListAPIView):
    # Получаем все статьи, отсортированные по дате публикации
    queryset = BlogPost.objects.order_by('-publication_date')
    serializer_class = BlogPostSerializer
    pagination_class = None

class BlogPostDetailAPIView(generics.RetrieveAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostDetailSerializer

class AllServicesListAPIView(generics.ListAPIView):
    queryset = Service.objects.all().order_by('parent_id', 'name')
    serializer_class = ServiceSerializer
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'parent']
    filterset_class = ServiceFilter
    
    search_fields = ['name', 'description']
    ordering_fields = ['base_price', 'name']
    
class RegisterAPIView(generics.GenericAPIView):
    """
    API для регистрации новых пользователей.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny] # Разрешаем анонимным пользователям регистрироваться

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # Проверяем, валидны ли данные
        serializer.is_valid(raise_exception=True) 
        # Сохраняем пользователя (вызывается метод .create() в сериализаторе)
        user = serializer.save()
        # Возвращаем успешный ответ
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "Пользователь успешно зарегистрирован."
        }, status=status.HTTP_201_CREATED)

class UserMeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
    
    
class OrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    # Доступ к этому API есть только у аутентифицированных пользователей
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Этот метод переопределяется для возврата списка заказов
        в зависимости от роли текущего пользователя.
        """
        user = self.request.user
        
        # Оптимизируем запросы сразу
        queryset = Order.objects.select_related('client', 'car', 'status').prefetch_related('performers')

        if user.roles.filter(name='Администратор').exists():
            # Администратор видит ВСЕ заказы
            return queryset.all()
        
        elif user.roles.filter(name='Автомеханик').exists():
            # Автомеханик видит заказы, где он назначен исполнителем
            return queryset.filter(performers=user)
            
        elif user.roles.filter(name='Клиент').exists():
            # Клиент видит только свои заказы
            return queryset.filter(client=user)
            
        # Если у пользователя нет ни одной из этих ролей, он не увидит ничего
        return Order.objects.none()
    
class OrderCreateAPIView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    # Только пользователи со статусом is_staff=True (админы) могут создавать заказы
    permission_classes = [IsAdminUser]
    

class ClientListAPIView(generics.ListAPIView):
    queryset = User.objects.filter(roles__name='Клиент').order_by('full_name')
    serializer_class = SimpleUserSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None

class CarListAPIView(generics.ListAPIView):
    queryset = ClientCar.objects.select_related('owner').all()
    serializer_class = SimpleClientCarSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None

class StatusListAPIView(generics.ListAPIView):
    queryset = OrderStatus.objects.all()
    serializer_class = SimpleOrderStatusSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None

class PerformerListAPIView(generics.ListAPIView):
    # Исполнители - это все сотрудники (is_staff=True)
    queryset = User.objects.filter(is_staff=True).order_by('full_name')
    serializer_class = SimpleUserSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None
    
class ServiceListForOrderAPIView(generics.ListAPIView):
    queryset = Service.objects.all().order_by('name')
    serializer_class = SimpleServiceSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None
    
class OrderDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API для просмотра, обновления и удаления одного конкретного заказа.
    """
    # Используем OrderSerializer для GET запросов (просмотр)
    serializer_class = OrderSerializer 
    # Доступ только для администраторов
    permission_classes = [IsAdminUser]
    # Оптимизируем queryset, как и в списке
    queryset = Order.objects.select_related('client', 'car', 'status').prefetch_related('performers').all()

    def get_serializer_class(self):
        """
        При обновлении (PUT/PATCH) используем сериализатор для создания/обновления,
        а при просмотре (GET) - обычный.
        """
        if self.request.method in ['PUT', 'PATCH']:
            return OrderCreateSerializer
        return super().get_serializer_class()
    
class OrderDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.select_related('client', 'car', 'status').prefetch_related('performers', 'order_items__service').all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return OrderCreateSerializer
        # Для GET запросов используем новый детальный сериализатор
        return OrderDetailSerializer
    
    
class ReviewListCreateAPIView(generics.ListCreateAPIView):
    """
    API для получения списка отзывов и создания нового.
    """
    queryset = Review.objects.select_related('user', 'order').prefetch_related('order__order_items__service').all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_permissions(self):
        # Для создания (POST) нужна аутентификация
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated]
        else:
            # Для просмотра (GET) разрешаем всем
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        """Переопределяем метод, чтобы добавить средний рейтинг в ответ."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        # Считаем средний рейтинг
        avg_rating = Review.objects.all().aggregate(Avg('rating'))['rating__avg'] or 0
        
        # Собираем кастомный ответ
        data = {
            'average_rating': round(avg_rating, 2),
            'reviews': serializer.data
        }
        return Response(data)

class ReviewDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API для просмотра, обновления и удаления отзыва.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewCreateSerializer
    # Используем наше кастомное право доступа
    permission_classes = [IsOwnerOrAdmin]

class UserOrderListAPIView(generics.ListAPIView):
    """
    Возвращает список заказов ТЕКУЩЕГО пользователя, на которые
    он может оставить отзыв (например, со статусом "Выполнен").
    """
    serializer_class = OrderSerializer # Можно создать более простой
    permission_classes = [IsAuthenticated]
    pagination_class = None
    
    def get_queryset(self):
        user = self.request.user
        # Находим ID заказов, на которые уже есть отзывы от этого пользователя
        reviewed_orders_ids = Review.objects.filter(user=user).values_list('order_id', flat=True)
        
        # Возвращаем заказы пользователя со статусом "Выполнен", исключая те, на которые уже есть отзыв
        return Order.objects.filter(
            client=user, 
            status__name="Завершен" 
        ).exclude(id__in=reviewed_orders_ids)