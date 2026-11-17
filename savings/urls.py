from django.urls import path
from . import views as v

urlpatterns = [
    path("", v.home, name="home"),
    path("owner/login/", v.owner_login, name="owner_login"),
    path("owner/logout/", v.owner_logout, name="owner_logout"),
    path("owner/", v.owner_dashboard, name="owner_dashboard"),
    path("owner/customers/<int:pk>/", v.owner_customer, name="owner_customer"),
    path("owner/customers/<int:pk>/delete/", v.delete_customer, name="delete_customer"),
    path("owner/deposits/<int:pk>/delete/", v.delete_deposit, name="delete_deposit"),
    path("login/", v.customer_login, name="customer_login"),
    path("logout/", v.customer_logout, name="customer_logout"),
    path("my-savings/", v.portal, name="portal"),
]
