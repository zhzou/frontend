from django.urls import path

from . import views

urlpatterns = [

#    path('adduser', views.adduser, name='adduser'),
#    path('verify', views.verify, name='verify'),
#    path('login', views.login, name='login'),
#    path('logout', views.logout, name='logout'),
    path('additem',views.additem,name='additem'),
    path('item/<str:iid>', views.item, name='insert_item'),
    path('search',views.search,name='search_item'),
    path('follow',views.follow,name='follow'),
    path('user/<str:username>',views.user,name='user'),
    path('user/<str:username>/followers',views.user_followers,name='followers'),
    path('user/<str:username>/following',views.user_following,name='following'),
    path('item/<str:iid>/like',views.like,name='following'),
    path('addmedia',views.addmedia,name='addmedia'),
    path('media/<str:iid>',views.media,name='media'),
]
