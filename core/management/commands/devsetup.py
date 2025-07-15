from django.core.management.base import BaseCommand
from django.core import management
import random

class Command(BaseCommand):
    help = "Apply migrations and start the dev server like a boss 😎"

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

        self.print_banner("LAUNCHING DONATIO SERVER")
        self.stdout.write(self.style.NOTICE(random.choice(self.JOKES)))
        self.stdout.write("")
        self.stdout.write(self.style.NOTICE("Step 2: Starting development server..."))
        self.stdout.write("=" * 50)
        management.call_command("runserver")

    def print_banner(self, title):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(f"{title.center(60)}")
        self.stdout.write("=" * 60 + "\n")
