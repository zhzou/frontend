from django.urls import path

from . import views

urlpatterns = [

    path('adduser/', views.adduser, name='adduser'),
    path('verify/', views.verify, name='verify'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('item/<int:iid>', views.item, name='item'),
]