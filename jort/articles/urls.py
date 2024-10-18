from django.urls import path
from .views import liste_articles, delete_article, add_article, contact

urlpatterns = [
    path('', liste_articles, name='liste_articles'),
    path('delete/<int:article_id>/', delete_article, name='delete_article'),
    path('add/', add_article, name='add_article'),
    path('contact/', contact, name='contact'),
]
