from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='index'),
    path('verify_page', views.verify, name='verify'),
    path('ssearch_main', views.search_main, name='ssearch_main'),
    path('additem_main', views.additem_main, name='additem_main'),
    path('sitem_main', views.item_main, name='sitem_main'),
    path('follow_main', views.follow_main, name='follow_main'),
    path('suser_main', views.user_main, name='suser_main'),
    path('sfollower_main', views.follower_main, name='sfollower_main'),
    path('sfollowing_main', views.following_main, name='sfollowing_main'),
    path('like_main', views.like_main, name='like_main'),
    path('unlike_main', views.unlike_main, name='unlike_main'),
    path('upload', views.upload, name='upload'),
    path('getmedia', views.getmedia, name='getmedia'),
    
]
