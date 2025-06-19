from django.db import migrations
import random


def create_roles_and_statuses(apps, schema_editor):
    """Создает базовые Роли и Статусы заказов."""
    Role = apps.get_model('atelier', 'Role')
    OrderStatus = apps.get_model('atelier', 'OrderStatus')

    roles = ["Клиент", "Менеджер", "Мастер-приемщик", "Автомеханик", "Специалист по детейлингу", "Администратор", "Маркетолог", "Электрик-диагност", "Специалист по стайлингу", "Бухгалтер"]
    for role_name in roles:
        Role.objects.get_or_create(name=role_name)

    statuses = ["Новый", "В работе", "Ожидает запчастей", "Готов к выдаче", "Завершен", "Отменен"]
    for status_name in statuses:
        OrderStatus.objects.get_or_create(name=status_name)


def create_users_and_cars(apps, schema_editor):
    """Создает Пользователей (сотрудников и клиентов) и их Автомобили."""
    User = apps.get_model('atelier', 'User')
    Role = apps.get_model('atelier', 'Role')
    ClientCar = apps.get_model('atelier', 'ClientCar')

    # --- Создаем сотрудников ---
    sidorova, _ = User.objects.get_or_create(
        email="sidorova_manager@example.com", defaults={'full_name': "Сидорова Анна Михайловна", 'is_staff': True}
    )
    sidorova.roles.add(Role.objects.get(name="Менеджер"), Role.objects.get(name="Администратор"))

    kuznetsov, _ = User.objects.get_or_create(
        email="kuznetsov_master@example.com", defaults={'full_name': "Кузнецов Сергей Викторович", 'is_staff': True}
    )
    kuznetsov.roles.add(Role.objects.get(name="Автомеханик"))

    mikhailov, _ = User.objects.get_or_create(
        email="mikhailov_detailer@example.com", defaults={'full_name': "Михайлов Дмитрий Алексеевич", 'is_staff': True}
    )
    mikhailov.roles.add(Role.objects.get(name="Специалист по детейлингу"))

    orlov, _ = User.objects.get_or_create(
        email="orlov_electric@example.com", defaults={'full_name': "Орлов Виктор Сергеевич", 'is_staff': True}
    )
    orlov.roles.add(Role.objects.get(name="Электрик-диагност"))

    pavlova, _ = User.objects.get_or_create(
        email="pavlova_styler@example.com", defaults={'full_name': "Павлова Ирина Олеговна", 'is_staff': True}
    )
    pavlova.roles.add(Role.objects.get(name="Специалист по стайлингу"))

    # --- Создаем клиентов и их машины ---
    client_data = [
        {"email": "ivanov@client.com", "full_name": "Иванов Иван", "cars": [("BMW", "X5", 2021), ("Audi", "A6", 2020)]},
        {"email": "petrov@client.com", "full_name": "Петров Петр", "cars": [("Mercedes-Benz", "C-Class", 2019)]},
        {"email": "smirnov@client.com", "full_name": "Смирнов Андрей", "cars": [("VW", "Tiguan", 2022), ("Audi", "RS7", 2022)]},
        {"email": "volkova@client.com", "full_name": "Волкова Елена", "cars": [("Toyota", "Camry", 2021), ("BMW", "M5", 2021)]},
        {"email": "morozov@client.com", "full_name": "Морозов Артем", "cars": [("Porsche", "911", 2023), ("Mercedes-AMG", "GT 63 S", 2022)]},
        {"email": "kozlov@client.com", "full_name": "Козлов Михаил", "cars": [("Subaru", "WRX STI", 2018)]},
        {"email": "fedorova@client.com", "full_name": "Федорова Светлана", "cars": [("Lexus", "LX570", 2020)]},
        {"email": "vasiliev@client.com", "full_name": "Васильев Дмитрий", "cars": [("Land Rover", "Defender", 2023)]},
        {"email": "semenova@client.com", "full_name": "Семенова Ольга", "cars": [("Kia", "K5", 2022)]},
        {"email": "bogdanov@client.com", "full_name": "Богданов Игорь", "cars": [("Genesis", "G80", 2021)]}
    ]

    client_role = Role.objects.get(name="Клиент")
    for data in client_data:
        client, _ = User.objects.get_or_create(email=data["email"], defaults={'full_name': data["full_name"]})
        client.roles.add(client_role)
        for make, model, year in data["cars"]:
            ClientCar.objects.get_or_create(
                owner=client, make=make, model=model, year_of_manufacture=year
            )


def create_services(apps, schema_editor):
    """Создает Категории услуг и сами Услуги."""
    ServiceCategory = apps.get_model('atelier', 'ServiceCategory')
    Service = apps.get_model('atelier', 'Service')

    categories_data = {
        "Чип-тюнинг": [("Stage 1 (бензин)", 25000), ("Stage 2 (бензин)", 45000)],
        "Стайлинг экстерьера": [("Оклейка винилом (полная)", 120000), ("Тонировка Lumar", 15000)],
        "Детейлинг": [("Полировка + керамика", 45000), ("Химчистка салона", 15000)],
        "Тюнинг выхлопной системы": [("Установка кат-бэка", 60000), ("Установка даунпайпа", 30000)],
        "Тюнинг подвески": [("Установка винтовой подвески", 85000), ("Установка пневмоподвески", 250000)],
        "Тормозная система": [("Замена тормозов (спорт)", 50000)],
        "Интерьер": [("Перетяжка салона кожей", 300000), ("Ambilight-подсветка", 35000)],
        "Автозвук": [("Процессорная аудиосистема", 150000), ("Шумоизоляция (полная)", 70000)],
        "Защитные покрытия": [("Оклейка полиуретаном", 200000)],
        "Диагностика": [("Компьютерная диагностика", 3000)]
    }

    for cat_name, services_list in categories_data.items():
        category, _ = ServiceCategory.objects.get_or_create(name=cat_name)
        for service_name, price in services_list:
            Service.objects.get_or_create(name=service_name, category=category, defaults={'base_price': price})


def create_orders_and_related(apps, schema_editor):
    """
    Создает 12 Заказов. Для первых 10 из них гарантированно создает
    Отзывы и Проекты портфолио.
    """
    # Получаем все необходимые модели
    Order = apps.get_model('atelier', 'Order')
    OrderItem = apps.get_model('atelier', 'OrderItem')
    User = apps.get_model('atelier', 'User')
    ClientCar = apps.get_model('atelier', 'ClientCar')
    Service = apps.get_model('atelier', 'Service')
    OrderStatus = apps.get_model('atelier', 'OrderStatus')
    Review = apps.get_model('atelier', 'Review')
    PortfolioProject = apps.get_model('atelier', 'PortfolioProject')

    # Заранее получаем списки объектов для ускорения работы
    clients = list(User.objects.filter(roles__name="Клиент"))
    staff = list(User.objects.filter(is_staff=True))
    services = list(Service.objects.all())
    status_completed = OrderStatus.objects.get(name="Завершен")
    
    # --- ГАРАНТИРОВАННОЕ СОЗДАНИЕ 10 ЗАКАЗОВ С ОТЗЫВАМИ И ПРОЕКТАМИ ПОРТФОЛИО ---
    for i in range(10):
        # Выбираем случайные данные для каждого заказа
        client = random.choice(clients)
        # Убедимся, что у клиента есть машина
        if not ClientCar.objects.filter(owner=client).exists():
            continue # Пропускаем итерацию, если у клиента нет машин
            
        car = ClientCar.objects.filter(owner=client).order_by('?').first()
        service = random.choice(services)
        performer = random.choice(staff)

        # Создаем завершенный заказ
        order = Order.objects.create(
            client=client,
            car=car,
            status=status_completed,
            total_cost=service.base_price,
            client_comment=f'Заказ #{i+1} на услугу "{service.name}". Все прошло отлично.'
        )
        # Добавляем исполнителя и позицию в заказ
        order.performers.add(performer)
        OrderItem.objects.create(order=order, service=service, item_price=service.base_price)
        
        # Создаем Отзыв для этого заказа
        Review.objects.create(
            order=order,
            user=client,
            review_text=f'Великолепный сервис! Особенно впечатлила работа над заказом #{order.id}. Буду рекомендовать друзьям.',
            rating=random.randint(4, 5)
        )
        
        # Создаем Проект Портфолио для этого заказа
        PortfolioProject.objects.create(
            project_name=f'Проект "{service.name}" для {car.make} {car.model}',
            work_description=f'В рамках проекта была выполнена услуга: {service.name}. Клиент остался очень доволен результатом.',
            base_order=order,
            car=car
        )

    # --- Создаем еще несколько заказов в других статусах для разнообразия ---
    status_in_progress = OrderStatus.objects.get(name="В работе")
    status_new = OrderStatus.objects.get(name="Новый")
    
    for _ in range(2): # Создаем 2 заказа в работе
        client=random.choice(clients)
        car = ClientCar.objects.filter(owner=client).first()
        if car:
            Order.objects.create(client=client, car=car, status=status_in_progress, client_comment='Заказ в процессе выполнения.')

    for _ in range(2): # Создаем 2 новых заказа
        client=random.choice(clients)
        car = ClientCar.objects.filter(owner=client).first()
        if car:
            Order.objects.create(client=client, car=car, status=status_new, client_comment='Новый заказ, ждет обработки.')


def create_blog_posts(apps, schema_editor):
    """Создает 10 статей для блога."""
    BlogPost = apps.get_model('atelier', 'BlogPost')
    User = apps.get_model('atelier', 'User')

    authors = list(User.objects.filter(is_staff=True))
    
    blog_data = [
        ("Что такое чип-тюнинг и зачем он нужен?", "Чип-тюнинг – это изменение программного обеспечения..."),
        ("Топ-5 ошибок при выборе виниловой пленки", "Оклейка автомобиля пленкой – популярный способ..."),
        ("Винтовая или пневмоподвеска: что выбрать?", "Выбор между винтовой и пневмоподвеской..."),
        ("Секреты идеальной полировки кузова", "Идеально гладкий и блестящий кузов - мечта..."),
        ("Как работает керамическое покрытие?", "Керамика - это не просто воск, это современное покрытие..."),
        ("Зачем нужна шумоизоляция в премиум-авто?", "Казалось бы, в дорогих автомобилях уже хорошая..."),
        ("Ambilight в салоне: создаем атмосферу", "Контурная подсветка салона - один из самых эффектных..."),
        ("Диагностика перед покупкой: что нужно знать", "Покупка подержанного автомобиля - всегда риск..."),
        ("Тюнинг выхлопной системы: от звука до мощности", "Выхлопная система влияет не только на звук..."),
        ("Полиуретан или винил: какую пленку выбрать?", "Оба материала служат для защиты и стайлинга...")
    ]

    for title, content in blog_data:
        BlogPost.objects.get_or_create(
            title=title,
            defaults={
                'content': content,
                'author': random.choice(authors)
            }
        )


class Migration(migrations.Migration):

    dependencies = [
        ('atelier', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_roles_and_statuses),
        migrations.RunPython(create_users_and_cars),
        migrations.RunPython(create_services),
        migrations.RunPython(create_orders_and_related),
        migrations.RunPython(create_blog_posts), 
    ]