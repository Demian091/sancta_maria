from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the business owner account (email + password login)."

    def add_arguments(self, parser):
        parser.add_argument("email")
        parser.add_argument("password")

    def handle(self, *args, **opts):
        User = get_user_model()
        email = opts["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            self.stderr.write("An account with that email already exists.")
            return
        User.objects.create_superuser(username=email, email=email, password=opts["password"])
        self.stdout.write(self.style.SUCCESS(f"Owner created: {email}"))
