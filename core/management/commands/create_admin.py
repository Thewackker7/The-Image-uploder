import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a superuser automatically from environment variables'

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not password:
            self.stdout.write(self.style.WARNING('DJANGO_SUPERUSER_PASSWORD not set. Skipping superuser creation.'))
            return

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser: {username}'))
        else:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.email = email
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated password for superuser: {username}'))
