from django.contrib import admin
from .models import Customer, Deposit

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "card_number", "phone")
    search_fields = ("name", "card_number")

@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ("customer", "date", "amount")
    list_filter = ("date",)
