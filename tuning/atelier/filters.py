# atelier/filters.py
import django_filters
from .models import Service, ServiceCategory

class ServiceFilter(django_filters.FilterSet):
    # Фильтр по категории. Мы используем ModelChoiceFilter, чтобы
    # DRF мог красиво отображать его в веб-интерфейсе API.
    # Фронтенд будет просто передавать ID категории.
    category = django_filters.ModelChoiceFilter(
        queryset=ServiceCategory.objects.all(),
        label="Категория"
    )

    class Meta:
        model = Service
        # Мы указываем только поле 'category', так как сортировка
        # будет обрабатываться отдельно.
        fields = ['category']