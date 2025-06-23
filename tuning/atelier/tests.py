# atelier/tests.py

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from .models import Service, ServiceCategory, Role, Order, OrderStatus, Review, ClientCar

User = get_user_model()


class CoreAPITests(APITestCase):
    """Набор из 10 ключевых тестов для проверки основного функционала API."""

    @classmethod
    def setUpTestData(cls):
        """
        Создаем начальные данные один раз для всех тестов этого класса.
        Это эффективнее, чем использовать setUp.
        """
        # --- Пользователи и роли ---
        cls.client_user_data = {'email': 'client@test.com', 'password': 'password123', 'full_name': 'Тест Клиент'}
        cls.another_user_data = {'email': 'another@test.com', 'password': 'password123', 'full_name': 'Другой Клиент'}
        
        cls.client_user = User.objects.create_user(**cls.client_user_data)
        cls.another_user = User.objects.create_user(**cls.another_user_data)
        
        client_role, _ = Role.objects.get_or_create(name='Клиент')
        cls.client_user.roles.add(client_role)
        cls.another_user.roles.add(client_role)
        
        # --- Услуги и категории ---
        cls.category = ServiceCategory.objects.create(name='Тестовая категория для фильтра')
        cls.service = Service.objects.create(name='Тест Услуга', category=cls.category, base_price=1000)
        
        # --- Заказы, статусы и отзывы ---
        cls.car = ClientCar.objects.create(owner=cls.client_user, make="Test", model="Car", year_of_manufacture=2020)
        cls.status_completed, _ = OrderStatus.objects.get_or_create(name='Завершен')
        
        cls.order_with_review = Order.objects.create(client=cls.client_user, car=cls.car, status=cls.status_completed)
        cls.order_without_review = Order.objects.create(client=cls.client_user, car=cls.car, status=cls.status_completed)
        
        cls.review = Review.objects.create(order=cls.order_with_review, user=cls.client_user, rating=5, review_text='Отличный сервис!')

        # --- URL-адреса ---
        cls.register_url = reverse('register-api')
        cls.login_url = reverse('rest_login')
        cls.services_url = reverse('all-services-list')
        cls.reviews_url = reverse('review-list-create')


    def setUp(self):
        """Настройка, которая выполняется перед каждым тестом."""
        self.client = APIClient()

    # --- ТЕСТЫ АУТЕНТИФИКАЦИИ (2) ---

    def test_1_user_registration_successful(self):
        """1. Тест: Успешная регистрация нового пользователя."""
        data = {'full_name': 'Новый Регистрант', 'email': 'registrant@example.com', 'password': 'newpassword123'}
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=data['email']).exists())
        new_user = User.objects.get(email=data['email'])
        self.assertTrue(new_user.roles.filter(name='Клиент').exists())

    def test_2_user_login_successful(self):
        """2. Тест: Успешный логин существующего пользователя."""
        data = {'email': self.client_user_data['email'], 'password': self.client_user_data['password']}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('key', response.data, "Токен аутентификации должен присутствовать в ответе.")

    # --- ТЕСТЫ ПУБЛИЧНОГО API (2) ---
    
    def test_3_get_public_data_service_list(self):
        """3. Тест: Анонимный пользователь может получить список услуг."""
        response = self.client.get(self.services_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreaterEqual(response.data['count'], 1)

    def test_4_filter_public_data_services(self):
        """4. Тест: Анонимный пользователь может фильтровать услуги по категории."""
        response = self.client.get(self.services_url, {'category': self.category.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Убедимся, что в результатах есть только наша тестовая услуга
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], self.service.name)

    # --- ТЕСТЫ ЗАЩИЩЕННОГО API И БИЗНЕС-ЛОГИКИ (6) ---

    def test_5_get_protected_data_orders(self):
        """5. Тест: Аутентифицированный пользователь получает список СВОИХ заказов."""
        self.client.force_authenticate(user=self.client_user)
        url = reverse('order-list') # Имя URL для списка заказов
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # В setUpTestData мы создали 2 заказа для этого пользователя
        self.assertEqual(response.data['count'], 2)

    def test_6_create_entity_review_successful(self):
        """6. Тест: Аутентифицированный пользователь может создать отзыв на свой заказ."""
        self.client.force_authenticate(user=self.client_user)
        data = {'order': self.order_without_review.id, 'rating': 4, 'review_text': 'Все было хорошо!'}
        response = self.client.post(self.reviews_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Review.objects.filter(order=self.order_without_review).exists())

    def test_7_create_review_for_another_user_order_forbidden(self):
        """7. Тест: Пользователь не может создать отзыв на чужой заказ."""
        self.client.force_authenticate(user=self.another_user) # Логинимся под другим пользователем
        data = {'order': self.order_with_review.id, 'rating': 1, 'review_text': 'Пытаюсь оставить отзыв на чужой заказ'}
        response = self.client.post(self.reviews_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_8_create_duplicate_review_forbidden(self):
        """8. Тест: Пользователь не может создать второй отзыв на один и тот же заказ."""
        self.client.force_authenticate(user=self.client_user)
        data = {'order': self.order_with_review.id, 'rating': 3, 'review_text': 'Пытаюсь оставить второй отзыв'}
        response = self.client.post(self.reviews_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("уже оставили отзыв", str(response.data))

    def test_9_delete_own_review_successful(self):
        """9. Тест: Пользователь может удалить свой собственный отзыв."""
        self.client.force_authenticate(user=self.client_user)
        url = reverse('review-detail', kwargs={'pk': self.review.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(pk=self.review.id).exists())
    
    def test_10_delete_another_user_review_forbidden(self):
        """10. Тест: Пользователь не может удалить чужой отзыв."""
        self.client.force_authenticate(user=self.another_user) # Логинимся под другим пользователем
        url = reverse('review-detail', kwargs={'pk': self.review.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)