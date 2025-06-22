# atelier/views_api.py
from rest_framework import generics
from .models import ServiceCategory, Service, PortfolioProject, BlogPost
from .serializers import ServiceCategorySerializer, ServiceSerializer, PortfolioProjectSerializer, BlogPostSerializer, BlogPostDetailSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from dj_rest_auth.registration.views import RegisterView 
from .serializers import RegisterSerializer, UserSerializer

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

class AllServicesListAPIView(generics.ListAPIView):
    queryset = Service.objects.all().order_by('parent_id', 'name')
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'parent']

class BlogPostDetailAPIView(generics.RetrieveAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostDetailSerializer

class AllServicesListAPIView(generics.ListAPIView):
    queryset = Service.objects.all().order_by('parent_id', 'name')
    serializer_class = ServiceSerializer
    
    filter_backends = [DjangoFilterBackend, SearchFilter] # Добавляем SearchFilter
    filterset_fields = ['category', 'parent']
    
    search_fields = ['name', 'description']
    
class CustomRegisterView(RegisterView):
    serializer_class = RegisterSerializer

class UserMeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user