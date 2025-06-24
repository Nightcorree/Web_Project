# atelier/serializers.py
from rest_framework import serializers
from .models import (
    Order, ServiceCategory, Service, PortfolioProject, 
    BlogPost, Role, OrderItem, User, ClientCar, OrderStatus, Review 
)
from django.contrib.auth import get_user_model
from dj_rest_auth.serializers import LoginSerializer as DefaultLoginSerializer

User = get_user_model()


# --- СЕРИАЛИЗАТОРЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ И АУТЕНТИФИКАЦИИ ---

class UserSerializer(serializers.ModelSerializer):
    roles = serializers.StringRelatedField(many=True, read_only=True)
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'phone_number', 'roles']

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'full_name')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'], 
            password=validated_data['password'],
            full_name=validated_data.get('full_name', '')
        )
        client_role, _ = Role.objects.get_or_create(name='Клиент')
        user.roles.add(client_role)
        return user

class CustomLoginSerializer(DefaultLoginSerializer):
    username = None


# --- СЕРИАЛИЗАТОРЫ ДЛЯ СПРАВОЧНИКОВ И ПРОСТЫХ СПИСКОВ ---

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name']

class SimpleClientCarSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    display_name = serializers.SerializerMethodField()
    class Meta:
        model = ClientCar
        fields = ['id', 'make', 'model', 'year_of_manufacture', 'owner_name', 'display_name']
    def get_display_name(self, obj):
        return str(obj)

class SimpleOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ['id', 'name']

class SimpleServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'base_price']

class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name']


# --- СЕРИАЛИЗАТОРЫ ДЛЯ ОСНОВНЫХ МОДЕЛЕЙ (Service, Project, Blog) ---

class ServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_on_sale_for_user = serializers.SerializerMethodField() 
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'base_price', 'promotional_price', 'category_name', 'is_on_sale_for_user']
    def get_is_on_sale_for_user(self, obj):
        request = self.context.get('request')
        user_is_logged_in = request and request.user.is_authenticated
        offer_is_active = obj.is_special_offer_active()
        return user_is_logged_in and offer_is_active

class PortfolioProjectSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(source='image', read_only=True)
    price = serializers.DecimalField(source='base_order.total_cost', max_digits=12, decimal_places=2, read_only=True, default=0)
    is_owner = serializers.SerializerMethodField()
    class Meta:
        model = PortfolioProject
        fields = ['id', 'project_name', 'work_description', 'price', 'image_url', 'is_owner']
    def get_is_owner(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated: return False
        if obj.base_order and obj.base_order.client: return obj.base_order.client.id == request.user.id
        return False

class BlogPostSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(source='image', read_only=True)
    short_content = serializers.SerializerMethodField()
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'short_content', 'image_url', 'publication_date']
    def get_short_content(self, obj):
        if len(obj.content) > 120: return obj.content[:120] + '...'
        return obj.content
    
class BlogPostDetailSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(source='image', read_only=True)
    author_name = serializers.CharField(source='author.full_name', read_only=True, default='Аноним')
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'content', 'image_url', 'publication_date', 'author_name']


# --- СЕРИАЛИЗАТОРЫ ДЛЯ ЗАКАЗОВ И ИХ ПОЗИЦИЙ ---

# Сериализатор для создания/обновления позиций
class OrderItemCreateSerializer(serializers.ModelSerializer):
    service_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = OrderItem
        fields = ['service_id', 'item_price', 'quantity', 'item_comment']

# Сериализатор для отображения позиций
class OrderItemDisplaySerializer(serializers.ModelSerializer):
    service_id = serializers.IntegerField(source='service.id', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    class Meta:
        model = OrderItem
        fields = ['service_id', 'service_name', 'item_price', 'quantity', 'item_comment']

# Сериализатор для создания/обновления заказа
class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления Заказов (Order).
    Обрабатывает вложенные позиции заказа (order_items) и одного исполнителя (performer).
    """
    order_items = OrderItemCreateSerializer(many=True)
    # Поле для приема ID одного исполнителя с фронтенда.
    # Оно не связано напрямую с моделью, поэтому write_only=True.
    # required=False и allow_null=True позволяют создавать заказ без исполнителя.
    performer_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Order
        # Убираем 'performers', так как будем обрабатывать его через 'performer_id'.
        fields = [
            'client', 'car', 'status', 'urgency', 
            'planned_completion_date', 'client_comment',
            'order_items', 'performer_id' 
        ]

    def create(self, validated_data):
        """
        Метод для СОЗДАНИЯ нового заказа.
        """
        order_items_data = validated_data.pop('order_items')
        performer_id = validated_data.pop('performer_id', None)
        
        order = Order.objects.create(**validated_data)

        if performer_id:
            try:
                performer = User.objects.get(id=performer_id)
                order.performers.set([performer]) # Привязываем одного исполнителя
            except User.DoesNotExist:
                # Можно добавить обработку, если исполнитель с таким ID не найден
                pass

        total_cost = 0
        for item_data in order_items_data:
            service = Service.objects.get(id=item_data.pop('service_id'))
            item_price = item_data.get('item_price', service.base_price)
            quantity = item_data.get('quantity', 1)
            OrderItem.objects.create(order=order, service=service, **item_data)
            total_cost += (item_price * quantity)
        
        order.total_cost = total_cost
        order.save()
        
        return order

    def update(self, instance, validated_data):
        """
        Метод для ОБНОВЛЕНИЯ существующего заказа.
        """
        order_items_data = validated_data.pop('order_items', None)
        performer_id = validated_data.pop('performer_id', None)
        
        instance = super().update(instance, validated_data)

        if performer_id is not None:
            if performer_id: # Если передан ID, устанавливаем исполнителя
                try:
                    performer = User.objects.get(id=performer_id)
                    instance.performers.set([performer])
                except User.DoesNotExist:
                    instance.performers.clear()
            else: # Если передан null или пустая строка, очищаем исполнителей
                instance.performers.clear()

        if order_items_data is not None:
            instance.order_items.all().delete()
            total_cost = 0
            for item_data in order_items_data:
                service = Service.objects.get(id=item_data.pop('service_id'))
                item_price = item_data.get('item_price', service.base_price)
                quantity = item_data.get('quantity', 1)
                OrderItem.objects.create(order=instance, service=service, **item_data)
                total_cost += (item_price * quantity)
            
            instance.total_cost = total_cost
            instance.save()

        return instance

    def update(self, instance, validated_data):
        """
        Метод для ОБНОВЛЕНИЯ существующего заказа.
        instance - это объект Order, который мы редактируем.
        """
        # 1. Извлекаем данные для вложенных и ManyToMany полей
        order_items_data = validated_data.pop('order_items', None)
        performers_data = validated_data.pop('performers', None)

        # 2. Обновляем простые поля заказа с помощью родительского метода
        instance = super().update(instance, validated_data)

        # 3. Обновляем исполнителей, если они были переданы
        if performers_data is not None:
            instance.performers.set(performers_data)

        # 4. Обновляем позиции заказа, если они были переданы
        if order_items_data is not None:
            # Простой и надежный способ: удаляем старые и создаем новые
            instance.order_items.all().delete()
            
            total_cost = 0
            for item_data in order_items_data:
                service = Service.objects.get(id=item_data.pop('service_id'))
                item_price = item_data.get('item_price', service.base_price)
                quantity = item_data.get('quantity', 1)
                OrderItem.objects.create(order=instance, service=service, **item_data)
                total_cost += (item_price * quantity)
            
            # 5. Пересчитываем и сохраняем итоговую стоимость
            instance.total_cost = total_cost
            instance.save()

        return instance

# Сериализатор для отображения списка заказов
class OrderSerializer(serializers.ModelSerializer):
    client = serializers.StringRelatedField(read_only=True)
    car = serializers.StringRelatedField(read_only=True)
    status = serializers.StringRelatedField(read_only=True)
    performers = serializers.StringRelatedField(many=True, read_only=True)
    urgency = serializers.CharField(source='get_urgency_display')
    class Meta:
        model = Order
        fields = ['id', 'client', 'car', 'status', 'urgency', 'created_at', 'planned_completion_date', 'total_cost', 'client_comment', 'performers']

# Сериализатор для детального отображения заказа
class OrderDetailSerializer(serializers.ModelSerializer):
    client = serializers.StringRelatedField()
    car = serializers.StringRelatedField()
    status = serializers.StringRelatedField()
    performers = SimpleUserSerializer(many=True, read_only=True)
    order_items = OrderItemDisplaySerializer(many=True, read_only=True) # Используем правильный сериализатор
    client_id = serializers.IntegerField(source='client.id')
    car_id = serializers.IntegerField(source='car.id')
    status_id = serializers.IntegerField(source='status.id')
    urgency_code = serializers.CharField(source='urgency', read_only=True) # Для предзаполнения select
    class Meta:
        model = Order
        fields = [
            'id', 'client', 'car', 'status', 'performers', 'order_items', 'urgency_code',
            'client_id', 'car_id', 'status_id', 'planned_completion_date', 
            'total_cost', 'client_comment'
        ]
        

class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения списка отзывов."""
    # Получаем строковые представления для удобства отображения
    user = serializers.StringRelatedField()
    # Мы покажем название первой услуги в заказе для простоты
    order_info = serializers.SerializerMethodField()
    # Добавляем ID пользователя для проверки прав на фронтенде
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'user_id', 'order_info', 'rating', 'review_text', 'review_date']
    
    def get_order_info(self, obj):
        # Для отзыва показываем ID заказа и название первой услуги
        first_item = obj.order.order_items.first()
        service_name = first_item.service.name if first_item else "Услуга не найдена"
        return f"Заказ #{obj.order.id} ({service_name})"


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания отзыва."""
    # При создании отзыва, user будет браться из request'а, его не нужно передавать
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Review
        # Нам нужны только эти поля для создания
        fields = ['id', 'order', 'rating', 'review_text', 'user']
    
    def validate_order(self, value):
        """Проверяем, что пользователь оставляет отзыв на СВОЙ заказ."""
        user = self.context['request'].user
        if value.client != user:
            raise serializers.ValidationError("Вы можете оставлять отзывы только на свои заказы.")
        
        # Проверяем, что на этот заказ еще нет отзыва от этого пользователя
        if Review.objects.filter(order=value, user=user).exists():
            raise serializers.ValidationError("Вы уже оставили отзыв на этот заказ.")
            
        return value