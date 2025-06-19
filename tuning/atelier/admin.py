# atelier/admin.py
from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Avg, Sum
from django.utils import timezone

from .models import (
    User, Role, ServiceCategory, Service, ClientCar,
    OrderStatus, Order, OrderItem, OrderPerformer,
    PortfolioProject, Review, BlogPost
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone_number', 'display_roles', 'get_created_orders_count', 'get_executed_orders_count')
    search_fields = ('full_name', 'email', 'phone_number')
    list_filter = ('roles',)
    filter_horizontal = ('roles',)

    @admin.display(description='Роли', ordering='roles__name') 
    def display_roles(self, obj):
        return ", ".join([role.name for role in obj.roles.all()])

    @admin.display(description='Создано заказов', ordering='created_orders_count_annotation')
    def get_created_orders_count(self, obj):
        return obj.created_orders_count_annotation

    @admin.display(description='Заказов в исполнении', ordering='executed_orders_count_annotation')
    def get_executed_orders_count(self, obj):
        return obj.executed_orders_count_annotation

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            created_orders_count_annotation=Count('created_orders', distinct=True),
            executed_orders_count_annotation=Count('executed_orders', distinct=True)
        )
        return qs


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
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
    def calculate_average_price_for_selected(self, request, queryset):
        aggregation = queryset.aggregate(avg_base_price=Avg('base_price'))
        avg_price = aggregation.get('avg_base_price')
        if avg_price is not None:
            self.message_user(request, f"Средняя базовая цена для выбранных услуг: {avg_price:.2f} руб.", messages.SUCCESS)
        else:
            self.message_user(request, "Не удалось рассчитать среднюю цену (возможно, не выбраны услуги или нет цен).", messages.WARNING)


@admin.register(ClientCar)
class ClientCarAdmin(admin.ModelAdmin):
    list_display = ('id', 'make', 'model', 'year_of_manufacture', 'display_vin_number', 'display_owner_link')
    search_fields = ('make', 'model', 'vin_number', 'owner__full_name', 'owner__email')
    list_filter = ('make', 'year_of_manufacture', 'owner')
    raw_id_fields = ('owner',)
    list_select_related = ('owner',)

    @admin.display(description='VIN', ordering='vin_number')
    def display_vin_number(self, obj):
        return obj.vin_number or "Не указан"

    @admin.display(description='Владелец', ordering='owner__full_name')
    def display_owner_link(self, obj):
        if obj.owner:
            link = reverse("admin:atelier_user_change", args=[obj.owner.id])
            return format_html('<a href="{}">{}</a>', link, obj.owner.full_name)
        return "-"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    raw_id_fields = ('service',)
    autocomplete_fields = ['service']
    verbose_name = "Позиция заказа" # Для инлайна
    verbose_name_plural = "Позиции заказа"


class OrderPerformerInline(admin.TabularInline):
    model = OrderPerformer
    extra = 1
    raw_id_fields = ('user',)
    autocomplete_fields = ['user']
    verbose_name = "Исполнитель заказа" # Для инлайна
    verbose_name_plural = "Исполнители заказа"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
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
    actions = ['calculate_total_sum_for_selected_orders']

    fieldsets = ( 
        (None, {
            'fields': ('client', 'car', 'status', 'urgency')
        }),
        ('Даты', {
            'fields': ('display_created_at_on_form', 'planned_completion_date'),
            'classes': ('collapse',)
        }),
        ('Финансы и комментарии', {
            'fields': ('display_calculated_total_cost', 'client_comment')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        current_year = timezone.now().year
        qs = qs.filter(created_at__year=current_year)
        qs = qs.exclude(status__name="Отменен")
        qs = qs.annotate(item_count_annotation=Count('order_items', distinct=True))
        qs = qs.order_by('urgency', '-created_at')
        return qs.prefetch_related('performers')

    @admin.display(description='Итоговая стоимость', ordering='total_cost')
    def display_total_cost(self, obj):
        return f"{obj.total_cost} руб." if obj.total_cost is not None else "Не рассчитана"

    @admin.display(description='Итоговая стоимость (расчет)')
    def display_calculated_total_cost(self, obj):
        return f"{obj.total_cost} руб." if obj.total_cost is not None else "Будет рассчитана"

    @admin.display(description='Клиент', ordering='client__full_name')
    def display_client_link(self, obj):
        if obj.client:
            link = reverse("admin:atelier_user_change", args=[obj.client.id])
            return format_html('<a href="{}">{}</a>', link, obj.client.full_name)
        return "-"

    @admin.display(description='Автомобиль', ordering='car__make')
    def display_car_link(self, obj):
        if obj.car:
            link = reverse("admin:atelier_clientcar_change", args=[obj.car.id])
            return format_html('<a href="{}">{}</a>', link, str(obj.car))
        return "-"

    @admin.display(description='Дата создания (в списке)', ordering='created_at')
    def display_created_at(self, obj):
        if obj.created_at:
            local_dt = timezone.localtime(obj.created_at)
            return local_dt.strftime("%d.%m.%Y %H:%M")
        return "-"
    
    @admin.display(description='Дата создания (на форме)')
    def display_created_at_on_form(self, obj):
        if obj.created_at:
            local_dt = timezone.localtime(obj.created_at)
            return local_dt.strftime("%d.%m.%Y %H:%M:%S %Z%z")
        return "-"

    @admin.display(description='Планируемая дата завершения', ordering='planned_completion_date')
    def display_planned_completion_date(self, obj):
        if obj.planned_completion_date:
            return obj.planned_completion_date.strftime("%d.%m.%Y")
        return "-"

    @admin.display(description='Исполнители')
    def display_performers_list(self, obj):
        return ", ".join([performer.full_name for performer in obj.performers.all()])

    @admin.display(description='Кол-во позиций', ordering='item_count_annotation')
    def get_item_count(self, obj):
        return obj.item_count_annotation
    
    @admin.action(description='Рассчитать общую стоимость для выбранных заказов') # Русский description
    def calculate_total_sum_for_selected_orders(self, request, queryset):
        aggregation = queryset.aggregate(total_sum=Sum('total_cost'))
        total = aggregation.get('total_sum')
        if total is not None:
            self.message_user(request, f"Общая итоговая стоимость для выбранных заказов: {total:.2f} руб.", messages.SUCCESS)
        else:
            self.message_user(request, "Не удалось рассчитать общую стоимость (возможно, стоимость не указана).", messages.WARNING)


@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(PortfolioProject)
class PortfolioProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'project_name', 'display_base_order_link', 'display_car_link_portfolio', 'display_publication_date')
    search_fields = ('project_name', 'work_description', 'base_order__id')
    list_filter = ('publication_date', 'car')
    date_hierarchy = 'publication_date'
    raw_id_fields = ('base_order', 'car')
    list_select_related = ('base_order', 'car')

    def get_queryset(self, request):
        return PortfolioProject.published.all()

    @admin.display(description='Заказ-основа', ordering='base_order__id')
    def display_base_order_link(self, obj):
        if obj.base_order:
            link = reverse("admin:atelier_order_change", args=[obj.base_order.id])
            return format_html('<a href="{}">Заказ №{}</a>', link, obj.base_order.id)
        return "-"

    @admin.display(description='Автомобиль', ordering='car__make')
    def display_car_link_portfolio(self, obj):
        if obj.car:
            link = reverse("admin:atelier_clientcar_change", args=[obj.car.id])
            return format_html('<a href="{}">{}</a>', link, str(obj.car))
        return "-"
    
    @admin.display(description='Дата публикации', ordering='publication_date')
    def display_publication_date(self, obj):
        if obj.publication_date:
            return obj.publication_date.strftime("%d.%m.%Y")
        return "-"

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_order_link_review', 'display_user_link_review', 'rating', 'display_review_date_list', 'display_short_review_text')
    list_filter = ('rating', 'review_date', 'user')
    search_fields = ('review_text', 'user__full_name', 'order__id')
    date_hierarchy = 'review_date'
    raw_id_fields = ('order', 'user')
    readonly_fields = ('display_review_date_form',)
    list_select_related = ('order', 'user', 'order__client', 'order__car')

    @admin.display(description='Заказ', ordering='order__id')
    def display_order_link_review(self, obj):
        if obj.order:
            link = reverse("admin:atelier_order_change", args=[obj.order.id])
            return format_html('<a href="{}">Заказ №{}</a>', link, obj.order.id)
        return "Заказ удален или не указан"

    @admin.display(description='Пользователь', ordering='user__full_name')
    def display_user_link_review(self, obj):
        if obj.user:
            link = reverse("admin:atelier_user_change", args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', link, obj.user.full_name)
        return "Пользователь удален или не указан"

    @admin.display(description='Дата отзыва (в списке)', ordering='review_date')
    def display_review_date_list(self, obj):
        if obj.review_date:
            local_dt = timezone.localtime(obj.review_date)
            return local_dt.strftime("%d.%m.%Y %H:%M")
        return "-"
        
    @admin.display(description='Дата отзыва (на форме)')
    def display_review_date_form(self, obj):
        if obj.review_date:
            local_dt = timezone.localtime(obj.review_date)
            return local_dt.strftime("%d.%m.%Y %H:%M:%S %Z%z")
        return "-"

    @admin.display(description='Текст отзыва')
    def display_short_review_text(self, obj):
        return (obj.review_text[:75] + '...') if len(obj.review_text) > 75 else obj.review_text


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'display_author_link_blog', 'display_publication_date_blog')
    list_filter = ('publication_date', 'author')
    search_fields = ('title', 'content', 'author__full_name')
    date_hierarchy = 'publication_date'
    raw_id_fields = ('author',)
    list_select_related = ('author',)

    @admin.display(description='Автор', ordering='author__full_name')
    def display_author_link_blog(self, obj):
        if obj.author:
            link = reverse("admin:atelier_user_change", args=[obj.author.id])
            return format_html('<a href="{}">{}</a>', link, obj.author.full_name)
        return "Не указан"

    @admin.display(description='Дата публикации', ordering='publication_date')
    def display_publication_date_blog(self, obj):
        if obj.publication_date:
            local_dt = timezone.localtime(obj.publication_date)
            return local_dt.strftime("%d.%m.%Y %H:%M")
        return "-"