# atelier/management/commands/add_subservices.py

from django.core.management.base import BaseCommand
from django.db import transaction
from atelier.models import Service # Импортируем нашу модель напрямую

class Command(BaseCommand):
    help = 'Находит существующие родительские услуги и создает для них подуслуги'

    # Словарь с подуслугами, которые мы хотим создать
    # Ключ - это уникальная часть названия СУЩЕСТВУЮЩЕЙ услуги
    SUB_SERVICES_MAP = {
        'Тонировка': [
            ("Тонировка фар", 4000), ("Атермальная тонировка", 18000),
            ("Электронная тонировка", 150000), ("Съемная тонировка", 5000),
        ],
        'Оклейка винилом': [
            ("Оклейка капота", 15000), ("Оклейка крыши (эффект панорамы)", 12000),
            ("Антихром", 25000), ("Оклейка зеркал", 5000),
        ],
        'Полировка': [
            ("Нанесение керамики (1 слой)", 15000), ("Нанесение жидкого стекла", 10000),
            ("Полировка одной детали", 2500), ("Полировка фар", 3000),
        ],
        'Химчистка': [
            ("Химчистка сидений", 6000), ("Химчистка потолка", 4000),
            ("Озонация салона", 2000), ("Кондиционер кожи", 1500),
        ],
        'Чип-тюнинг': [
            ("Отключение EGR", 8000), ("Снятие ограничителя скорости", 5000),
            ("Прошивка под Евро-2", 7000), ("Адаптация АКПП", 6000),
        ],
        'выхлопа': [
            ("Установка даунпайпа", 15000), ("Разводка выхлопа на 2 стороны", 25000),
            ("Установка насадок", 8000), ("Замена катализатора на пламегаситель", 12000),
        ],
        'подвески': [
            ("Установка винтовой подвески (coilovers)", 15000), ("Установка пневмоподвески", 30000),
            ("Замена пружин с занижением", 8000), ("Установка стабилизаторов", 10000),
        ],
        'Перетяжка салона': [
            ("Перетяжка руля", 8000), ("Перетяжка потолка в алькантару", 50000),
            ("Перетяжка сидений (2 шт)", 70000), ("Аквапринт деталей салона", 20000),
        ],
        'аудиосистемы': [
            ("Установка сабвуфера", 8000), ("Установка усилителя", 7000),
            ("Замена штатной акустики", 12000), ("Изготовление подиумов", 20000),
        ],
        'полиуретаном': [
            ("Защита фар", 5000), ("Защита зон под ручками", 2000),
            ("Оклейка порогов", 6000), ("Оклейка переднего бампера", 25000),
        ]
    }

    @transaction.atomic # Оборачиваем в транзакцию: если что-то пойдет не так, все изменения откатятся
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- Начало создания подуслуг ---'))
        
        created_count = 0
        skipped_parents = 0

        for parent_keyword, subservices_list in self.SUB_SERVICES_MAP.items():
            try:
                # Находим родительскую услугу
                parent_service = Service.objects.get(name__icontains=parent_keyword, parent__isnull=True)
                self.stdout.write(f'Найден родитель: "{parent_service.name}"')

                # Создаем для нее подуслуги
                for sub_service_name, sub_price in subservices_list:
                    service, created = Service.objects.get_or_create(
                        name=sub_service_name,
                        category=parent_service.category,
                        parent=parent_service,
                        defaults={'base_price': sub_price}
                    )
                    if created:
                        created_count += 1
                        self.stdout.write(f'  -> Создана подуслуга: "{sub_service_name}"')
                    else:
                        self.stdout.write(f'  -> Подуслуга "{sub_service_name}" уже существует. Пропускаем.')

            except Service.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'ПРЕДУПРЕЖДЕНИЕ: Родительская услуга со словом "{parent_keyword}" не найдена. Пропускаем.'))
                skipped_parents += 1
            except Service.MultipleObjectsReturned:
                self.stdout.write(self.style.WARNING(f'ПРЕДУПРЕЖДЕНИЕ: Найдено несколько услуг со словом "{parent_keyword}". Пропускаем, чтобы избежать ошибок.'))
                skipped_parents += 1
        
        self.stdout.write(self.style.SUCCESS(f'--- Завершено ---'))
        self.stdout.write(self.style.SUCCESS(f'Создано новых подуслуг: {created_count}'))
        if skipped_parents > 0:
            self.stdout.write(self.style.WARNING(f'Не найдено родительских услуг: {skipped_parents}'))