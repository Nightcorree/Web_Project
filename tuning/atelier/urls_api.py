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
]