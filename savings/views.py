import calendar
from functools import wraps
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CustomerForm, CustomerLoginForm, DepositForm, OwnerLoginForm
from .models import Customer, Deposit, normalize_name
from .utils import month_statement, year_summary

MONTHS = [(i, calendar.month_name[i]) for i in range(1, 13)]


def owner_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_authenticated and request.user.is_staff):
            return redirect("owner_login")
        return view(request, *args, **kwargs)
    return wrapper


def customer_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        cid = request.session.get("customer_id")
        customer = Customer.objects.filter(pk=cid).first() if cid else None
        if not customer:
            return redirect("customer_login")
        return view(request, customer, *args, **kwargs)
    return wrapper


def _statement_context(customer, request):
    today = timezone.localdate()
    try:
        year, month = int(request.GET.get("year", today.year)), int(request.GET.get("month", today.month))
        if not (1 <= month <= 12 and 2000 <= year <= 2100):
            raise ValueError
    except ValueError:
        year, month = today.year, today.month
    return {"customer": customer, "year": year, "month": month, "months": MONTHS,
            "years": range(today.year - 5, today.year + 3),
            "st": month_statement(customer, year, month),
            "year_rows": year_summary(customer, year)}


def home(request):
    return render(request, "savings/home.html")


# ---------- Owner ----------
def owner_login(request):
    form = OwnerLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(request, username=form.cleaned_data["email"],
                            password=form.cleaned_data["password"])
        if user and user.is_staff:
            login(request, user)
            return redirect("owner_dashboard")
        messages.error(request, "Invalid email or password.")
    return render(request, "savings/owner_login.html", {"form": form})


@require_POST
def owner_logout(request):
    logout(request)
    return redirect("home")


@owner_required
def owner_dashboard(request):
    form = CustomerForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        c = form.save()
        messages.success(request, f"Customer {c.name} added.")
        return redirect("owner_customer", pk=c.pk)
    q = request.GET.get("q", "").strip()
    customers = Customer.objects.annotate(total=Coalesce(Sum("deposits__amount"), Decimal("0")))
    if q:
        customers = customers.filter(Q(name__icontains=q) | Q(card_number__icontains=q))
    grand = Deposit.objects.aggregate(s=Sum("amount"))["s"] or Decimal("0")
    return render(request, "savings/owner_dashboard.html",
                  {"customers": customers, "form": form, "q": q, "grand": grand})


@owner_required
def owner_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = DepositForm(request.POST or None, initial={"date": timezone.localdate()})
    if request.method == "POST" and form.is_valid():
        dep = form.save(commit=False)
        dep.customer = customer
        dep.save()
        messages.success(request, f"₦{dep.amount:,.2f} saved for {dep.date:%d %b %Y}.")
        return redirect(f"{request.path}?year={dep.date.year}&month={dep.date.month}")
    ctx = _statement_context(customer, request)
    ctx.update({"form": form, "is_owner": True,
                "recent": customer.deposits.all()[:15]})
    return render(request, "savings/owner_customer.html", ctx)


@owner_required
@require_POST
def delete_deposit(request, pk):
    dep = get_object_or_404(Deposit, pk=pk)
    cid = dep.customer_id
    dep.delete()
    messages.success(request, "Deposit removed.")
    return redirect("owner_customer", pk=cid)


@owner_required
@require_POST
def delete_customer(request, pk):
    get_object_or_404(Customer, pk=pk).delete()
    messages.success(request, "Customer deleted.")
    return redirect("owner_dashboard")


# ---------- Customer ----------
def customer_login(request):
    form = CustomerLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        customer = Customer.objects.filter(
            name_lower=normalize_name(form.cleaned_data["name"]),
            card_number=form.cleaned_data["card_number"].strip()).first()
        if customer:
            request.session.flush()
            request.session["customer_id"] = customer.pk
            return redirect("portal")
        messages.error(request, "Name and card number do not match.")
    return render(request, "savings/customer_login.html", {"form": form})


@require_POST
def customer_logout(request):
    request.session.flush()
    return redirect("home")


@customer_required
def portal(request, customer):
    return render(request, "savings/portal.html", _statement_context(customer, request))
