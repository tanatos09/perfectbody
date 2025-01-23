from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = "Nastavení databáze: migrace, inicializace dat a nahrání fixtur."

    def handle(self, *args, **kwargs):
        self.stdout.write("Spouštím migrace...")
        call_command("makemigrations")
        call_command("migrate")

        self.stdout.write("Inicializuji základní data...")
        call_command("initialize_data")

        self.stdout.write("Server nastaven!")
