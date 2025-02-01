"""
URL configuration for cafe project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path("", views.index, name="index"),
    path("accounts/", views.admin_login, name="admin_login"),
    path("users/", views.user_management, name="user_management"),
    path("create_user/", views.create_user, name="create_user"),
    path("remove_user/<int:user_id>/", views.remove_user, name="remove_user"),
    path("update_user/<int:user_id>/", views.update_user, name="update_user"),
    path("items/", views.item_list, name="item_list"),
    path("items/create/", views.create_item, name="create_item"),
    path("items/update/<int:item_id>/", views.update_item, name="update_item"),
    path("items/delete/<int:item_id>/", views.remove_item, name="remove_item"),
    path("orders/", views.order_management, name="order_management"),
    path("create_order/", views.create_order, name="create_order"),
    path("order_report/", views.order_report, name="order_report"),
    path("order/<int:order_id>/delete/", views.order_delete, name="order_delete"),
    path("order/update/<int:order_id>/", views.update_order, name="update_order"),
    path("order/update/<int:order_id>/", views.update_order, name="update_order"),
]
