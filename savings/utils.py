import calendar
from datetime import date
from decimal import Decimal
from django.db.models import Sum

ZERO = Decimal("0")


def month_statement(customer, year, month):
    """Every day of the month: amount saved that day + cumulative balance."""
    first = date(year, month, 1)
    opening = customer.deposits.filter(date__lt=first).aggregate(s=Sum("amount"))["s"] or ZERO
    per_day = {r["date"]: r["s"] for r in
               customer.deposits.filter(date__year=year, date__month=month)
               .values("date").annotate(s=Sum("amount"))}
    rows, running = [], opening
    for d in range(1, calendar.monthrange(year, month)[1] + 1):
        day = date(year, month, d)
        amt = per_day.get(day, ZERO)
        running += amt
        rows.append({"date": day, "deposit": amt, "balance": running})
    return {"opening": opening, "rows": rows, "total": running - opening, "closing": running}


def year_summary(customer, year):
    """Per-month totals and closing balance for the whole year."""
    running = customer.deposits.filter(date__lt=date(year, 1, 1)).aggregate(s=Sum("amount"))["s"] or ZERO
    totals = {}
    for dep in customer.deposits.filter(date__year=year):
        totals[dep.date.month] = totals.get(dep.date.month, ZERO) + dep.amount
    rows = []
    for m in range(1, 13):
        t = totals.get(m, ZERO)
        running += t
        rows.append({"month": m, "name": calendar.month_name[m], "total": t, "balance": running})
    return rows
