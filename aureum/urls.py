from django.urls import path
from . import views
urlpatterns = [
    path("", views.home, name='home'),
    path("information", views.information, name='information'),
    path("income", views.income, name='income'),
    path("balance", views.balance, name='balance'),
    path("cash", views.cash, name='cash'),
]

'''
path("cash", views.cash, name='cash'),
path("balance", views.balance, name='balance'),
path("income", views.income, name='income'),
'''
