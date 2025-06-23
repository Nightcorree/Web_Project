# atelier/urls_api.py
from django.urls import path
from . import views_api

urlpatterns = [
    path('service-categories/', views_api.ServiceCategoryListAPIView.as_view(), name='service-category-list'),
    path('services/', views_api.ServiceListAPIView.as_view(), name='service-list'),
    path('portfolio/recent/', views_api.RecentPortfolioProjectsAPIView.as_view(), name='recent-portfolio-list'),
    path('blog/recent/', views_api.RecentBlogPostsAPIView.as_view(), name='recent-blog-list'), 
    path('portfolio/all/', views_api.PortfolioProjectListAPIView.as_view(), name='portfolio-list-all'),
    path('blog/all/', views_api.BlogPostListAPIView.as_view(), name='blog-list-all'),
    path('service-categories/', views_api.ServiceCategoryListAPIView.as_view(), name='service-category-list'),
    path('services/all/', views_api.AllServicesListAPIView.as_view(), name='all-services-list'),
    path('blog/<int:pk>/', views_api.BlogPostDetailAPIView.as_view(), name='blog-post-detail'),
    path('users/me/', views_api.UserMeView.as_view(), name='user-me'),
    path('orders/', views_api.OrderListAPIView.as_view(), name='order-list'),
    path('orders/create/', views_api.OrderCreateAPIView.as_view(), name='order-create'),
    path('form-data/clients/', views_api.ClientListAPIView.as_view()),
    path('form-data/cars/', views_api.CarListAPIView.as_view()),
    path('form-data/statuses/', views_api.StatusListAPIView.as_view()),
    path('form-data/performers/', views_api.PerformerListAPIView.as_view()),
    path('form-data/services/', views_api.ServiceListForOrderAPIView.as_view()),
    path('orders/<int:pk>/', views_api.OrderDetailAPIView.as_view(), name='order-detail'),
    # НОВЫЙ URL ДЛЯ ЭКЗАМЕНОВ
    path('mfexams/', views_api.MFexamListAPIView.as_view(), name='mfexam-list'),
]