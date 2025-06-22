# atelier/serializers.py
from rest_framework import serializers, generics
from .models import ServiceCategory, Service, PortfolioProject, BlogPost, Role
from django.contrib.auth import get_user_model



User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    # Получаем названия ролей, а не их ID
    roles = serializers.StringRelatedField(many=True, read_only=True)
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'phone_number', 'roles']


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'full_name')
        extra_kwargs = {'password': {'write_only': True}} # Пароль не будет возвращаться в ответе

    def create(self, validated_data):
        # Создаем пользователя с хешированным паролем
        user = User.objects.create_user(
            validated_data['email'], 
            validated_data['password'],
            full_name=validated_data['full_name']
        )
        # По умолчанию присваиваем роль "Клиент"
        client_role, _ = Role.objects.get_or_create(name='Клиент')
        user.roles.add(client_role)
        return user
 


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name']

class ServiceSerializer(serializers.ModelSerializer):
    # Если вы хотите показывать и название категории услуги
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Service
        # Указываем поля, которые нужны на фронтенде
        fields = ['id', 'name', 'description', 'base_price', 'category_name']

class PortfolioProjectSerializer(serializers.ModelSerializer):
    # Получаем URL изображения
    image_url = serializers.ImageField(source='image', read_only=True)
    # Получаем цену из связанного заказа
    price = serializers.DecimalField(source='base_order.total_cost', max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = PortfolioProject
        fields = ['id', 'project_name', 'work_description', 'price', 'image_url']


class BlogPostSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(source='image', read_only=True)
    # Создаем поле с коротким содержанием
    short_content = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'short_content', 'image_url', 'publication_date']

    def get_short_content(self, obj):
        # Обрезаем текст до 120 символов для превью
        if len(obj.content) > 120:
            return obj.content[:120] + '...'
        return obj.content
    
class BlogPostDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для одной статьи, с полным содержанием."""
    image_url = serializers.ImageField(source='image', read_only=True)
    author_name = serializers.CharField(source='author.full_name', read_only=True, default='Аноним')

    class Meta:
        model = BlogPost
        # Включаем ПОЛНЫЙ 'content' и добавляем имя автора для наглядности
        fields = ['id', 'title', 'content', 'image_url', 'publication_date', 'author_name']
        
        
