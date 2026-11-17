from django import forms
from .models import Customer, Deposit


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "card_number", "phone"]


class DepositForm(forms.ModelForm):
    class Meta:
        model = Deposit
        fields = ["date", "amount", "note"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}


class OwnerLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class CustomerLoginForm(forms.Form):
    name = forms.CharField(max_length=150)
    card_number = forms.CharField(max_length=30)
