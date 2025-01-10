from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = "Inicializace základních dat (skupiny, defaultní nastavení atd.)"

    def handle(self, *args, **kwargs):
        group_name = "trainer"
        trainer_group, created = Group.objects.get_or_create(name=group_name)
        if created:
            self.stdout.write(f"Skupina '{group_name}' byla vytvořena.")
        else:
            self.stdout.write(f"Skupina '{group_name}' již existuje.")