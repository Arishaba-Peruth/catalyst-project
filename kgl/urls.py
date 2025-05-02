"""
URL configuration for kgl project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from homeapp import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('allstock/', views.allstock, name='allstock'),
    path('home/<int:stock_id>/', views.stock_detail, name='stock_detail'),
    path('sell_item/<str:pk>/',views.sell_item, name='sell_item'),
    path('receipt/',views.receipt, name='receipt'),
    path('login/', views.Login, name='login'),
    path('allsales/', views.allsales, name='allsales'),
    path('addstock/', views.addstock, name='addstock'),
    path('addstock/<str:pk>/', views.addstock, name='update_stock'),
    path('addsales/<int:pk>/', views.addsales, name='addsales'),
    path('deferredpayment/', views.deferredpayment, name='deferredpayment'),
    path('adddcreditpayment/', views.add_deferredpayment, name='add_deferredpayment'),
    path('edit/<int:pk>/',views.editsalespage, name='edit'),
    path('view/<int:pk>', views.viewpage, name='view'),
    path('delete/<int:pk>', views.deteletransaction, name='delete'),
    path('receipt/<int:receipt_id>/',views.receipt_detail, name='receipt_detail'),
    path('dashboard/', views.manager, name='manager'),
    path('viewcredit/<int:pk>/', views.viewcredit, name='viewcredit'),
    path('editcredit/<int:pk>/', views.editcredit, name='editcredit'),
    path('deletecredit/<int:pk>/', views.deletecredit, name='deletecredit'),
    path('createstock/', views.createstock, name='createstock'),
    path('dashboard2/', views.salesagent, name='salesagent'),
    path('dashboard3/', views.director, name='director'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
]
