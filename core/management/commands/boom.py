from django.core.management.base import BaseCommand
from django.core import management
from allauth.account.models import EmailAddress
from accounts.models import User, Profile
import random


class Command(BaseCommand):
    help = "Apply migrations, create users with verified emails & profiles, and start the dev server like a boss 😎"

    JOKES = [
        "🛠️  Running migrations... fingers crossed nothing breaks!",
        "🧙‍♂️  May the ORM be with you...",
        "⚙️  Applying migrations like it's 1999.",
        "💻  Time to wake up the dev server!",
        "🚀  Launching into development mode!",
        "🐞  Expect bugs. Debugging is just part of the adventure.",
        "📦  Setting things up... did you forget to activate your venv? 😅",
        "🌈  Django magic incoming!",
        "🥲  Please don't be that one migration that breaks everything...",
    ]

    def handle(self, *args, **kwargs):
        self.print_banner("MIGRATION TIME")
        self.stdout.write(self.style.NOTICE(random.choice(self.JOKES)))
        self.stdout.write("")
        self.stdout.write(self.style.NOTICE("Step 1: Applying migrations..."))
        self.stdout.write("=" * 50)
        management.call_command("migrate")
        self.stdout.write("")

        self.stdout.write(self.style.NOTICE("Step 2: Creating users with verified emails & profiles..."))
        self.stdout.write("=" * 50)
        self.create_users()
        self.stdout.write("")

        self.print_banner("LAUNCHING DONATIO SERVER")
        self.stdout.write(self.style.NOTICE(random.choice(self.JOKES)))
        self.stdout.write("")
        self.stdout.write(self.style.NOTICE("Step 3: Starting development server..."))
        self.stdout.write("=" * 50)
        management.call_command("runserver")

    def print_banner(self, title):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(f"{title.center(60)}")
        self.stdout.write("=" * 60 + "\n")

    def create_users(self):
        users_data = [
            {
                "username": "admin",
                "email": "admin@gmail.com",
                "password": "password123",
                "is_superuser": True,
                "is_staff": True,
                "full_name": "Super Admin",
                "phone_number": "0999999999"
            },
            {
                "username": "bot1",
                "email": "bot1@gmail.com",
                "password": "password123",
                "is_superuser": False,
                "is_staff": False,
                "full_name": "John Doe",
                "phone_number": "0912345678"
            },
            {
                "username": "bot2",
                "email": "bot2@gmail.com",
                "password": "password123",
                "is_superuser": False,
                "is_staff": False,
                "full_name": "Jane Doe",
                "phone_number": "0987654321"
            },
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data["username"],
                defaults={
                    "email": user_data["email"],
                    "is_staff": user_data["is_staff"],
                    "is_superuser": user_data["is_superuser"],
                }
            )

            if created:
                user.set_password(user_data["password"])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"✅ Created user '{user.username}'"))

            else:
                self.stdout.write(self.style.WARNING(f"⚠️ User '{user.username}' already exists"))

            # Ensure verified email
            email_obj, email_created = EmailAddress.objects.get_or_create(
                user=user,
                email=user.email,
                defaults={"verified": True, "primary": True}
            )

            if not email_created and not email_obj.verified:
                email_obj.verified = True
                email_obj.primary = True
                email_obj.save()
                self.stdout.write(self.style.SUCCESS(f"📨 Verified email for '{user.username}'"))
            elif email_created:
                self.stdout.write(self.style.SUCCESS(f"📨 Email added and verified for '{user.username}'"))
            else:
                self.stdout.write(self.style.NOTICE(f"✔️ Email already verified for '{user.username}'"))

            # Ensure profile
            profile, profile_created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    "full_name": user_data["full_name"],
                    "phone_number": user_data["phone_number"],
                }
            )
            if profile_created:
                self.stdout.write(self.style.SUCCESS(f"👤 Profile created for '{user.username}'"))
            else:
                self.stdout.write(self.style.NOTICE(f"👤 Profile already exists for '{user.username}'"))
