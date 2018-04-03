from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='index'),
    path('verify_page', views.verify, name='verify'),
    path('search_main', views.search_main, name='search_main'),
    path('additem_main', views.additem_main, name='additem_main'),
    path('item_main', views.item_main, name='item_main'),
    path('follow_main', views.follow_main, name='follow_main'),
]