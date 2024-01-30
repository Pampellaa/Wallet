"""
URL configuration for ProjectKoncowy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from wallet import views
from wallet.views import AddMoneyToSavingsView, SavingsDeleteView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.IndexView.as_view(), name='index'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('income/', views.IncomeView.as_view(), name='income'),
    path('expense/', views.ExpenseView.as_view(), name='expense'),
    path('income-add/', views.IncomeAddView.as_view(), name='income_add'),
    path('expense-add/', views.ExpenseAddView.as_view(), name='expense_add'),
    path('category/', views.CategoryView.as_view(), name='category'),
    path('category-add/', views.CategoryAddView.as_view(), name='category_add'),
    path('savings/', views.SavingsView.as_view(), name='savings'),
    path('savings-add/', views.SavingsAddView.as_view(), name='savings_add'),
    path('add_money/<int:saving_id>/', AddMoneyToSavingsView.as_view(), name='add_money_to_savings'),
    path('savings-delete/<int:saving_id>/', SavingsDeleteView.as_view(), name='savings_delete'),

]
