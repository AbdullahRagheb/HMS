from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a super admin user if one does not already exist'

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(role='super_admin').exists():
            try:
                super_admin = User.objects.create_user(
                    username='superadmin',
                    email='superadmin@example.com',
                    password='superadmin123',
                    role='super_admin'
                )
                super_admin.is_staff = True  # Grants access to the Django admin interface
                super_admin.is_superuser = True  # Grants full permissions
                super_admin.save()
                self.stdout.write(self.style.SUCCESS('Super Admin created successfully'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating Super Admin: {str(e)}'))
        else:
            self.stdout.write(self.style.WARNING('Super Admin already exists'))