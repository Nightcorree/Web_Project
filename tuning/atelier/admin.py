# atelier/admin.py
from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Avg, Sum, QuerySet
from django.utils import timezone
from django.http import HttpRequest
from typing import List, Optional

from .models import (
    User, Role, ServiceCategory, Service, ClientCar,
    OrderStatus, Order, OrderItem, OrderPerformer,
    PortfolioProject, Review, BlogPost
)

from django.http import HttpResponse
from django.utils.html import format_html
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings
import os

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админ-панель для модели User."""
    list_display = ('id', 'full_name', 'email', 'phone_number', 'display_roles', 'get_created_orders_count', 'get_executed_orders_count')
    search_fields = ('full_name', 'email', 'phone_number')
    list_filter = ('roles',)
    filter_horizontal = ('roles',)
    
    actions = ['analyze_and_modify_users']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональная информация', {'fields': ('full_name', 'phone_number', 'social_link')}), # <-- Добавили social_link
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Роли в системе', {'fields': ('roles',)}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    
    
    @admin.action(description="Проанализировать и модифицировать выбранных пользователей")
    def analyze_and_modify_users(self, request: HttpRequest, queryset: QuerySet[User]) -> None:
        """
        Комплексное действие для демонстрации различных методов ORM.
        """
        
        # 1. Демонстрация exists()
        # Проверяем, есть ли среди выбранных неактивные пользователи
        if queryset.filter(is_active=False).exists():
            self.message_user(request, "Внимание: Среди выбранных есть неактивные пользователи.", messages.WARNING)
        
        # 2. Демонстрация __icontains и count()
        # Ищем пользователей, у которых в имени есть "иван" (без учета регистра)
        users_with_ivan_count = queryset.filter(full_name__icontains='иван').count()
        if users_with_ivan_count > 0:
            self.message_user(request, f"Найдено пользователей с именем 'Иван': {users_with_ivan_count} шт.", messages.INFO)
            
        # 3. Демонстрация values()
        # Получаем словари с email и ролями. Вывод будет в консоли сервера.
        # Обратите внимание, как __ для получения поля из связанной модели.
        users_data = queryset.values('email', 'roles__name')
        print("\n--- Данные выбранных пользователей (метод values) ---")
        for data in users_data:
            print(data)

        # 4. Демонстрация values_list()
        # Получаем "плоский" список всех email адресов выбранных пользователей.
        email_list = queryset.values_list('email', flat=True)
        print("\n--- Список email выбранных пользователей (метод values_list) ---")
        print(list(email_list))

        # 5. Демонстрация update()
        # Для всех выбранных пользователей, у кого не заполнена ссылка на соцсеть,
        # устанавливаем заглушку. Метод update() возвращает количество обновленных записей.
        updated_count = queryset.filter(social_link='').update(social_link='http://example.com/placeholder')
        self.message_user(request, f"Обновлено профилей без соцсети: {updated_count} шт.", messages.SUCCESS)

        # 6. Демонстрация delete()
        # ИСПРАВЛЕНИЕ 2: Удаляем неактивных пользователей (is_active=False),
        # у которых нет заказов. Исключаем суперпользователей для безопасности.
        users_to_delete = queryset.filter(is_active=False, is_superuser=False, created_orders__isnull=True)
        if users_to_delete.exists():
            deleted_count, _ = users_to_delete.delete()
            self.message_user(request, f"Удалено неактивных пользователей без заказов: {deleted_count} шт.", messages.ERROR)
        else:
             self.message_user(request, "Не найдено неактивных пользователей без заказов для удаления.", messages.INFO)

    @admin.display(description='Роли', ordering='roles__name') 
    def display_roles(self, obj: User) -> str:
        """Отображает роли пользователя через запятую."""
        return ", ".join([role.name for role in obj.roles.all()])

    @admin.display(description='Создано заказов', ordering='created_orders_count_annotation')
    def get_created_orders_count(self, obj: User) -> int:
        """Возвращает количество созданных пользователем заказов."""
        return obj.created_orders_count_annotation

    @admin.display(description='Заказов в исполнении', ordering='executed_orders_count_annotation')
    def get_executed_orders_count(self, obj: User) -> int:
        """Возвращает количество выполненных пользователем заказов."""
        return obj.executed_orders_count_annotation

    def get_queryset(self, request: HttpRequest) -> QuerySet[User]:
        """Добавляет аннотации для сортировки по количеству заказов."""
        qs = super().get_queryset(request)
        qs = qs.annotate(
            created_orders_count_annotation=Count('created_orders', distinct=True),
            executed_orders_count_annotation=Count('executed_orders', distinct=True)
        )
        return qs


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Админ-панель для модели Role."""
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    """Админ-панель для модели ServiceCategory."""
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Админ-панель для модели Service."""
    list_display = ('id', 'name', 'category', 'base_price', 'promotional_price', 'promotion_ends_on', 'is_special_offer_active')
    list_filter = ('category', 'promotion_ends_on')
    search_fields = ('name', 'description', 'category__name')
    raw_id_fields = ('category',)
    list_select_related = ('category',)
    fieldsets = (
        (None, {'fields': ('name', 'category', 'description')}),
        ('Ценообразование', {'fields': ('base_price', 'promotional_price', 'promotion_ends_on')}), 
    )
    actions = ['calculate_average_price_for_selected']

    @admin.action(description='Рассчитать среднюю базовую цену для выбранных') 
    def calculate_average_price_for_selected(self, request: HttpRequest, queryset: QuerySet[Service]) -> None:
        """Action для расчета средней цены выбранных услуг."""
        aggregation = queryset.aggregate(avg_base_price=Avg('base_price'))
        avg_price = aggregation.get('avg_base_price')
        if avg_price is not None:
            self.message_user(request, f"Средняя базовая цена для выбранных услуг: {avg_price:.2f} руб.", messages.SUCCESS)
        else:
            self.message_user(request, "Не удалось рассчитать среднюю цену (возможно, не выбраны услуги или нет цен).", messages.WARNING)


@admin.register(ClientCar)
class ClientCarAdmin(admin.ModelAdmin):
    """Админ-панель для модели ClientCar."""
    list_display = ('id', 'make', 'model', 'year_of_manufacture', 'display_vin_number', 'display_owner_link')
    search_fields = ('make', 'model', 'vin_number', 'owner__full_name', 'owner__email')
    list_filter = ('make', 'year_of_manufacture', 'owner')
    raw_id_fields = ('owner',)
    list_select_related = ('owner',)

    @admin.display(description='VIN', ordering='vin_number')
    def display_vin_number(self, obj: ClientCar) -> str:
        """Отображает VIN-номер или заглушку."""
        return obj.vin_number or "Не указан"

    @admin.display(description='Владелец', ordering='owner__full_name')
    def display_owner_link(self, obj: ClientCar) -> str:
        """Отображает ссылку на владельца автомобиля."""
        if obj.owner:
            link = reverse("admin:atelier_user_change", args=[obj.owner.id])
            return format_html('<a href="{}">{}</a>', link, obj.owner.full_name)
        return "-"


class OrderItemInline(admin.TabularInline):
    """Инлайн для отображения позиций заказа в админке Order."""
    model = OrderItem
    extra = 1
    raw_id_fields = ('service',)
    autocomplete_fields = ['service']
    verbose_name = "Позиция заказа"
    verbose_name_plural = "Позиции заказа"


class OrderPerformerInline(admin.TabularInline):
    """Инлайн для отображения исполнителей заказа в админке Order."""
    model = OrderPerformer
    extra = 1
    raw_id_fields = ('user',)
    autocomplete_fields = ['user']
    verbose_name = "Исполнитель заказа"
    verbose_name_plural = "Исполнители заказа"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Админ-панель для модели Order."""
    list_display = ('id', 'display_client_link', 'display_car_link', 'status', 'urgency', 'display_created_at', 
                    'display_planned_completion_date', 'display_total_cost', 'display_performers_list', 'get_item_count')
    list_filter = ('status', 'urgency', 'created_at', 'planned_completion_date', 'client', 'car')
    search_fields = ('id', 'client__full_name', 'client__email', 'car__vin_number', 'car__make', 
                     'car__model', 'client_comment', 'status__name')
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline, OrderPerformerInline]
    raw_id_fields = ('client', 'car', 'status')
    readonly_fields = ('display_created_at_on_form', 'display_calculated_total_cost')
    list_select_related = ('client', 'car', 'status')
    list_display_links = ('id', 'display_client_link')
    actions = ['calculate_total_sum_for_selected_orders', 'generate_order_pdf_action']

    fieldsets = ( 
        (None, {
            'fields': ('client', 'car', 'status', 'urgency', 'image', 'work_report')
        }),
        ('Даты', {
            'fields': ('display_created_at_on_form', 'planned_completion_date'),
            'classes': ('collapse',)
        }),
        ('Финансы и комментарии', {
            'fields': ('display_calculated_total_cost', 'client_comment')
        }),
    )
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Order]:
        """Фильтрует и аннотирует queryset заказов."""
        qs = super().get_queryset(request)
        qs = qs.exclude(status__name="Отменен")
        qs = qs.annotate(item_count_annotation=Count('order_items', distinct=True))
        qs = qs.order_by('urgency', '-created_at')
        return qs.prefetch_related('performers')

    @admin.display(description='Итоговая стоимость', ordering='total_cost')
    def display_total_cost(self, obj: Order) -> str:
        """Отображает итоговую стоимость заказа."""
        return f"{obj.total_cost} руб." if obj.total_cost is not None else "Не рассчитана"

    @admin.display(description='Итоговая стоимость (расчет)')
    def display_calculated_total_cost(self, obj: Order) -> str:
        """Отображает расчетную стоимость на форме редактирования."""
        return f"{obj.total_cost} руб." if obj.total_cost is not None else "Будет рассчитана"

    @admin.display(description='Клиент', ordering='client__full_name')
    def display_client_link(self, obj: Order) -> str:
        """Отображает ссылку на клиента."""
        if obj.client:
            link = reverse("admin:atelier_user_change", args=[obj.client.id])
            return format_html('<a href="{}">{}</a>', link, obj.client.full_name)
        return "-"

    @admin.display(description='Автомобиль', ordering='car__make')
    def display_car_link(self, obj: Order) -> str:
        """Отображает ссылку на автомобиль."""
        if obj.car:
            link = reverse("admin:atelier_clientcar_change", args=[obj.car.id])
            return format_html('<a href="{}">{}</a>', link, str(obj.car))
        return "-"

    @admin.display(description='Дата создания (в списке)', ordering='created_at')
    def display_created_at(self, obj: Order) -> str:
        """Отображает форматированную дату создания в списке."""
        if obj.created_at:
            local_dt = timezone.localtime(obj.created_at)
            return local_dt.strftime("%d.%m.%Y %H:%M")
        return "-"
    
    @admin.display(description='Дата создания (на форме)')
    def display_created_at_on_form(self, obj: Order) -> str:
        """Отображает форматированную дату создания на форме."""
        if obj.created_at:
            local_dt = timezone.localtime(obj.created_at)
            return local_dt.strftime("%d.%m.%Y %H:%M:%S %Z%z")
        return "-"

    @admin.display(description='Планируемая дата завершения', ordering='planned_completion_date')
    def display_planned_completion_date(self, obj: Order) -> str:
        """Отображает форматированную дату завершения."""
        if obj.planned_completion_date:
            return obj.planned_completion_date.strftime("%d.%m.%Y")
        return "-"

    @admin.display(description='Исполнители')
    def display_performers_list(self, obj: Order) -> str:
        """Отображает список исполнителей через запятую."""
        return ", ".join([performer.full_name for performer in obj.performers.all()])

    @admin.display(description='Кол-во позиций', ordering='item_count_annotation')
    def get_item_count(self, obj: Order) -> int:
        """Возвращает количество позиций в заказе."""
        return obj.item_count_annotation
    
    @admin.action(description='Рассчитать общую стоимость для выбранных заказов')
    def calculate_total_sum_for_selected_orders(self, request: HttpRequest, queryset: QuerySet[Order]) -> None:
        """Action для расчета общей стоимости выбранных заказов."""
        aggregation = queryset.aggregate(total_sum=Sum('total_cost'))
        total = aggregation.get('total_sum')
        if total is not None:
            self.message_user(request, f"Общая итоговая стоимость для выбранных заказов: {total:.2f} руб.", messages.SUCCESS)
        else:
            self.message_user(request, "Не удалось рассчитать общую стоимость (возможно, стоимость не указана).", messages.WARNING)
            
    @admin.action(description="Сформировать PDF для заказа")
    def generate_order_pdf_action(self, request: HttpRequest, queryset: QuerySet[Order]) -> HttpResponse | None:
        """
        Действие для генерации PDF-документа с деталями заказа.
        Работает только для одного выбранного заказа.
        """
        if queryset.count() != 1:
            self.message_user(request, "Пожалуйста, выберите только один заказ для генерации PDF.", messages.WARNING)
            return

        order = queryset.first()
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="order_{order.id}.pdf"'

        try:
            # Строим абсолютный путь к файлу шрифта
            font_path = os.path.join(settings.BASE_DIR, 'atelier', 'static', 'atelier', 'fonts', 'DejaVuSans.ttf')
            pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
            font_name = 'DejaVuSans'
        except Exception:
            # Если шрифт не найден, используем стандартный
            self.message_user(request, "Шрифт DejaVuSans не найден, текст может отображаться некорректно.", messages.WARNING)
            font_name = 'Helvetica'


        p = canvas.Canvas(response, pagesize=letter)
        p.setFont(font_name, 12)

        p.drawString(2*cm, 25*cm, f"Заказ-наряд №: {order.id}")
        p.drawString(2*cm, 24*cm, f"Дата создания: {order.created_at.strftime('%d.%m.%Y')}")
        p.line(2*cm, 23.5*cm, 19*cm, 23.5*cm)

        p.drawString(2*cm, 22.5*cm, f"Клиент: {order.client.full_name}")
        p.drawString(2*cm, 22*cm, f"Автомобиль: {order.car}")
        p.drawString(2*cm, 21.5*cm, f"Статус: {order.status.name}")
        p.line(2*cm, 21*cm, 19*cm, 21*cm)

        p.drawString(2*cm, 20*cm, "Перечень работ/услуг:")
        y = 19.5
        for item in order.order_items.all():
            p.drawString(2.5*cm, y*cm, f"- {item.service.name} (x{item.quantity})")
            y -= 0.7
            if y < 3:
                p.showPage()
                p.setFont(font_name, 12)
                y = 25

        y -= 1
        p.line(2*cm, y*cm, 19*cm, y*cm)
        y -= 1
        p.setFont(font_name, 14)
        p.drawString(12*cm, y*cm, f"Итого: {order.total_cost} руб.")

        p.showPage()
        p.save()
        
        return response


@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    """Админ-панель для модели OrderStatus."""
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(PortfolioProject)
class PortfolioProjectAdmin(admin.ModelAdmin):
    """Админ-панель для модели PortfolioProject."""
    list_display = ('id', 'project_name', 'display_base_order_link', 'display_car_link_portfolio', 'display_publication_date')
    search_fields = ('project_name', 'work_description', 'base_order__id')
    list_filter = ('publication_date', 'car')
    date_hierarchy = 'publication_date'
    raw_id_fields = ('base_order', 'car')
    list_select_related = ('base_order', 'car')

    def get_queryset(self, request: HttpRequest) -> QuerySet[PortfolioProject]:
        """Возвращает только опубликованные проекты."""
        return PortfolioProject.published.all()

    @admin.display(description='Заказ-основа', ordering='base_order__id')
    def display_base_order_link(self, obj: PortfolioProject) -> str:
        """Отображает ссылку на заказ-основу."""
        if obj.base_order:
            link = reverse("admin:atelier_order_change", args=[obj.base_order.id])
            return format_html('<a href="{}">Заказ №{}</a>', link, obj.base_order.id)
        return "-"

    @admin.display(description='Автомобиль', ordering='car__make')
    def display_car_link_portfolio(self, obj: PortfolioProject) -> str:
        """Отображает ссылку на автомобиль проекта."""
        if obj.car:
            link = reverse("admin:atelier_clientcar_change", args=[obj.car.id])
            return format_html('<a href="{}">{}</a>', link, str(obj.car))
        return "-"
    
    @admin.display(description='Дата публикации', ordering='publication_date')
    def display_publication_date(self, obj: PortfolioProject) -> str:
        """Отображает форматированную дату публикации."""
        if obj.publication_date:
            return obj.publication_date.strftime("%d.%m.%Y")
        return "-"

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Админ-панель для модели Review."""
    list_display = ('id', 'display_order_link_review', 'display_user_link_review', 'rating', 'display_review_date_list', 'display_short_review_text')
    list_filter = ('rating', 'review_date', 'user')
    search_fields = ('review_text', 'user__full_name', 'order__id')
    date_hierarchy = 'review_date'
    raw_id_fields = ('order', 'user')
    readonly_fields = ('display_review_date_form',)
    list_select_related = ('order', 'user', 'order__client', 'order__car')

    @admin.display(description='Заказ', ordering='order__id')
    def display_order_link_review(self, obj: Review) -> str:
        """Отображает ссылку на заказ, к которому оставлен отзыв."""
        if obj.order:
            link = reverse("admin:atelier_order_change", args=[obj.order.id])
            return format_html('<a href="{}">Заказ №{}</a>', link, obj.order.id)
        return "Заказ удален или не указан"

    @admin.display(description='Пользователь', ordering='user__full_name')
    def display_user_link_review(self, obj: Review) -> str:
        """Отображает ссылку на автора отзыва."""
        if obj.user:
            link = reverse("admin:atelier_user_change", args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', link, obj.user.full_name)
        return "Пользователь удален или не указан"

    @admin.display(description='Дата отзыва (в списке)', ordering='review_date')
    def display_review_date_list(self, obj: Review) -> str:
        """Отображает форматированную дату отзыва в списке."""
        if obj.review_date:
            local_dt = timezone.localtime(obj.review_date)
            return local_dt.strftime("%d.%m.%Y %H:%M")
        return "-"
        
    @admin.display(description='Дата отзыва (на форме)')
    def display_review_date_form(self, obj: Review) -> str:
        """Отображает форматированную дату отзыва на форме."""
        if obj.review_date:
            local_dt = timezone.localtime(obj.review_date)
            return local_dt.strftime("%d.%m.%Y %H:%M:%S %Z%z")
        return "-"

    @admin.display(description='Текст отзыва')
    def display_short_review_text(self, obj: Review) -> str:
        """Отображает сокращенный текст отзыва."""
        return (obj.review_text[:75] + '...') if len(obj.review_text) > 75 else obj.review_text


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """Админ-панель для модели BlogPost."""
    list_display = ('id', 'title', 'display_author_link_blog', 'display_publication_date_blog')
    list_filter = ('publication_date', 'author')
    search_fields = ('title', 'content', 'author__full_name')
    date_hierarchy = 'publication_date'
    raw_id_fields = ('author',)
    list_select_related = ('author',)

    @admin.display(description='Автор', ordering='author__full_name')
    def display_author_link_blog(self, obj: BlogPost) -> str:
        """Отображает ссылку на автора статьи."""
        if obj.author:
            link = reverse("admin:atelier_user_change", args=[obj.author.id])
            return format_html('<a href="{}">{}</a>', link, obj.author.full_name)
        return "Не указан"

    @admin.display(description='Дата публикации', ordering='publication_date')
    def display_publication_date_blog(self, obj: BlogPost) -> str:
        """Отображает форматированную дату публикации статьи."""
        if obj.publication_date:
            local_dt = timezone.localtime(obj.publication_date)
            return local_dt.strftime("%d.%m.%Y %H:%M")
        return "-"