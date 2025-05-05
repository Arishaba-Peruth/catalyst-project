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
    #view for landing page--------------
    path('', views.index, name='index'),
    #view for all stock page-------------------
    path('allstock/', views.allstock, name='allstock'),
    #view for all stock detail page//////////////
    path('home/<int:stock_id>/', views.stock_detail, name='stock_detail'),
    #view for all sell or issue out  page------------
    path('sell_item/<str:pk>/',views.sell_item, name='sell_item'),
    #view for all receipts page//////////////////
    path('receipt/',views.receipt, name='receipt'),
    #view for all login page---------------------
    path('login/', views.Login, name='login'),
    #view for allsales page\\\\\\\\\\\\\\\\\\
    path('allsales/', views.allsales, name='allsales'),
    #view for all add stock page------------------
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
