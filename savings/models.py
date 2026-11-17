from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone


def normalize_name(value: str) -> str:
    """Lower-case and collapse spaces so 'Mary  ANN' and 'mary ann' match."""
    return " ".join(value.lower().split())


class Customer(models.Model):
    name = models.CharField(max_length=150)
    name_lower = models.CharField(max_length=150, editable=False, db_index=True)
    card_number = models.CharField(max_length=30, unique=True)
    phone = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name_lower"]

    def save(self, *args, **kwargs):
        self.name_lower = normalize_name(self.name)
        super().save(*args, **kwargs)

    @property
    def balance(self):
        return self.deposits.aggregate(s=Sum("amount"))["s"] or Decimal("0")

    def __str__(self):
        return f"{self.name} ({self.card_number})"


class Deposit(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="deposits")
    date = models.DateField(default=timezone.localdate)
    amount = models.DecimalField(max_digits=12, decimal_places=2,
                                 validators=[MinValueValidator(Decimal("0.01"))])
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.customer.name}: {self.amount} on {self.date}"
