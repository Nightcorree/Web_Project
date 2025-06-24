# atelier/filters.py
import django_filters
from .models import Service, ServiceCategory

class ServiceFilter(django_filters.FilterSet):
    category = django_filters.ModelChoiceFilter(
        queryset=ServiceCategory.objects.all(),
        label="Категория"
    )

    class Meta:
        model = Service
        fields = ['category']