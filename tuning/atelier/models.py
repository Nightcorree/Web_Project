# atelier/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager
from typing import Optional, List

class CustomUserManager(BaseUserManager):
    """
    Кастомный менеджер для модели User, где email является уникальным
    идентификатором для аутентификации вместо username.
    """
    def create_user(self, email: str, password: str, **extra_fields) -> "User":
        """Создает и сохраняет пользователя с указанным email и паролем.

        Args:
            email (str): Email пользователя.
            password (str): Пароль пользователя.
            **extra_fields: Дополнительные поля.

        Returns:
            User: Созданный объект пользователя.

        Raises:
            ValueError: Если email не предоставлен.
        """
        if not email:
            raise ValueError('Поле Email должно быть установлено')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields) -> "User":
        """Создает и сохраняет суперпользователя с указанным email и паролем.

        Args:
            email (str): Email суперпользователя.
            password (str): Пароль суперпользователя.
            **extra_fields: Дополнительные поля.

        Returns:
            User: Созданный объект суперпользователя.
        
        Raises:
            ValueError: Если is_staff или is_superuser не равны True.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Модель кастомного пользователя."""
    username = None 
    email = models.EmailField(unique=True, verbose_name="Email")
    
    first_name = None
    last_name = None
    full_name = models.CharField(max_length=255, verbose_name="ФИО", blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")
    roles = models.ManyToManyField('Role', blank=True, verbose_name="Роли")
    
    social_link = models.URLField(
        max_length=200, 
        blank=True, 
        verbose_name="Ссылка на соцсеть"
    )

    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
 
    def __str__(self) -> str:
        """Возвращает строковое представление пользователя."""
        return self.full_name or self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['full_name']


class Role(models.Model):
    """Модель роли пользователя (Клиент, Администратор и т.д.)."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название роли")

    def __str__(self) -> str:
        """Возвращает строковое представление роли."""
        return self.name

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"
        ordering = ['name']


class ServiceCategory(models.Model):
    """Модель категории услуг."""
    name = models.CharField(max_length=150, unique=True, verbose_name="Название категории")

    def __str__(self) -> str:
        """Возвращает строковое представление категории услуг."""
        return self.name

    class Meta:
        verbose_name = "Категория услуг"
        verbose_name_plural = "Категории услуг"
        ordering = ['name']


class Service(models.Model):
    """Модель услуги, предоставляемой ателье."""
    name = models.CharField(max_length=200, verbose_name="Название услуги")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Базовая цена")
    category = models.ForeignKey(ServiceCategory, on_delete=models.PROTECT, verbose_name="Категория")

    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='sub_services',
        verbose_name="Родительская услуга"
    )

    promotional_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Акционная цена")
    promotion_ends_on = models.DateField(blank=True, null=True, verbose_name="Акция действует до")

    def is_special_offer_active(self) -> bool:
        """Проверяет, активна ли акция на данный момент.

        Returns:
            bool: True, если акция активна, иначе False.
        """
        if self.promotional_price is not None and self.promotion_ends_on is not None:
            return timezone.now().date() <= self.promotion_ends_on
        return False
    is_special_offer_active.boolean = True
    is_special_offer_active.short_description = "Акция активна?"

    def __str__(self) -> str:
        """Возвращает строковое представление услуги."""
        return self.name

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ['category__name', 'name']


class ClientCar(models.Model):
    """Модель автомобиля клиента."""
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец")
    make = models.CharField(max_length=100, verbose_name="Марка")
    model = models.CharField(max_length=100, verbose_name="Модель")
    year_of_manufacture = models.PositiveSmallIntegerField(verbose_name="Год выпуска")
    vin_number = models.CharField(max_length=17, unique=True, blank=True, null=True, verbose_name="VIN-номер")

    def __str__(self) -> str:
        """Возвращает строковое представление автомобиля."""
        return f"{self.make} {self.model} ({self.year_of_manufacture})"

    class Meta:
        verbose_name = "Автомобиль клиента"
        verbose_name_plural = "Автомобили клиентов"
        ordering = ['make', 'model']


class OrderStatus(models.Model):
    """Модель статуса заказа (например, "В работе", "Завершен")."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название статуса")

    def __str__(self) -> str:
        """Возвращает строковое представление статуса."""
        return self.name

    class Meta:
        verbose_name = "Статус заказа"
        verbose_name_plural = "Статусы заказов"
        ordering = ['name']


class Order(models.Model):
    """Модель заказа на выполнение работ."""
    client = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Клиент", related_name="created_orders")
    car = models.ForeignKey(ClientCar, on_delete=models.PROTECT, verbose_name="Автомобиль")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    planned_completion_date = models.DateField(blank=True, null=True, verbose_name="Планируемая дата завершения")
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Итоговая стоимость")
    client_comment = models.TextField(blank=True, null=True, verbose_name="Комментарий клиента")
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT, verbose_name="Статус")
    performers = models.ManyToManyField(
        User,
        through='OrderPerformer',
        verbose_name="Исполнители",
        related_name="executed_orders",
        blank=True
    )
    
    image = models.ImageField(
        upload_to='service_images/', 
        blank=True, 
        null=True, 
        verbose_name="Изображение услуги"
    )
    
    work_report = models.FileField(
        upload_to='order_reports/', 
        blank=True, 
        null=True, 
        verbose_name="Отчет по работам"
    )

    class Urgency(models.TextChoices):
        """Перечисление уровней срочности заказа."""
        NORMAL = 'NRM', 'Обычная' 
        URGENT = 'URG', 'Срочная'
        VERY_URGENT = 'VUR', 'Очень срочная (вне очереди)'

    urgency = models.CharField(
        max_length=3,
        choices=Urgency.choices,
        default=Urgency.NORMAL,
        verbose_name="Срочность заказа"
    )

    def __str__(self) -> str:
        """Возвращает строковое представление заказа."""
        return f"Заказ №{self.pk} от {self.created_at.strftime('%d.%m.%Y')}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']


class OrderItem(models.Model):
    """Модель позиции в заказе (конкретная услуга)."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items", verbose_name="Заказ")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, verbose_name="Услуга")
    item_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена позиции")
    item_comment = models.TextField(blank=True, null=True, verbose_name="Комментарий к позиции")
    quantity = models.PositiveSmallIntegerField(default=1, verbose_name="Количество")

    def __str__(self) -> str:
        """Возвращает строковое представление позиции заказа."""
        return f"{self.service.name} для заказа №{self.order.pk}"

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"
        unique_together = (('order', 'service'),)


class OrderPerformer(models.Model):
    """Промежуточная модель для связи Заказа и Исполнителя."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Исполнитель")
    role_in_order = models.CharField(max_length=100, blank=True, null=True, verbose_name="Роль сотрудника в заказе")

    def __str__(self) -> str:
        """Возвращает строковое представление связи."""
        return f"{self.user.full_name} - исполнитель заказа №{self.order.pk}"

    class Meta:
        verbose_name = "Исполнитель заказа"
        verbose_name_plural = "Исполнители заказов"
        unique_together = (('order', 'user'),)


class PortfolioProjectManager(models.Manager):
    """Кастомный менеджер для проектов портфолио."""
    def get_queryset(self):
        """Возвращает только опубликованные и корректно заполненные проекты."""
        return super().get_queryset().filter(
            base_order__isnull=False,
            car__isnull=False,
            publication_date__lte=timezone.now().date() 
        ).order_by('-publication_date')

    def recent_projects(self, count: int = 3):
        """Возвращает несколько последних опубликованных проектов.

        Args:
            count (int): Количество проектов для возврата.
        """
        return self.get_queryset()[:count]


class PortfolioProject(models.Model):
    """Модель проекта в портфолио."""
    project_name = models.CharField(max_length=200, verbose_name="Название проекта")
    work_description = models.TextField(verbose_name="Описание доработок")
    image = models.ImageField(upload_to='portfolio_images/', blank=True, null=True, verbose_name="Изображение проекта")
    publication_date = models.DateField(default=timezone.now, verbose_name="Дата публикации")
    base_order = models.OneToOneField(Order, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Заказ-основа")
    car = models.ForeignKey(ClientCar, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Демонстрируемый автомобиль")
    
    objects = models.Manager()
    published = PortfolioProjectManager()

    def __str__(self) -> str:
        """Возвращает строковое представление проекта."""
        return self.project_name

    class Meta:
        verbose_name = "Проект портфолио"
        verbose_name_plural = "Проекты портфолио"


class Review(models.Model):
    """Модель отзыва клиента на заказ."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор отзыва")
    review_text = models.TextField(verbose_name="Текст отзыва")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка (1-5)"
    )
    review_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата отзыва")

    def __str__(self) -> str:
        """Возвращает строковое представление отзыва."""
        return f"Отзыв от {self.user.full_name} для заказа №{self.order.pk}"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-review_date']


class BlogPost(models.Model):
    """Модель статьи в блоге."""
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True, verbose_name="Изображение для статьи")
    publication_date = models.DateTimeField(default=timezone.now, verbose_name="Дата публикации")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Автор")

    def __str__(self) -> str:
        """Возвращает строковое представление статьи."""
        return self.title

    class Meta:
        verbose_name = "Статья блога"
        verbose_name_plural = "Статьи блога"
        ordering = ['-publication_date']