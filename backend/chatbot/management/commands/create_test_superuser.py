"""
Django management command to create a test superuser for CISO Assistant.
This is useful for development, testing, and demo purposes.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction


class Command(BaseCommand):
    help = 'Create a test superuser for development and testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='admin@admin.test',
            help='Email address for the superuser (default: admin@admin.test)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='Admintest123',
            help='Password for the superuser (default: Admintest123)'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='Admin',
            help='First name for the superuser (default: Admin)'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='User',
            help='Last name for the superuser (default: User)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force creation even if user already exists (will update password)'
        )

    def handle(self, *args, **options):
        User = get_user_model()
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        force = options['force']

        self.stdout.write(f"Creating test superuser with email: {email}")

        try:
            with transaction.atomic():
                # Check if user already exists
                if User.objects.filter(email=email).exists():
                    if not force:
                        self.stdout.write(
                            self.style.WARNING(
                                f'User with email {email} already exists. '
                                'Use --force to update the existing user.'
                            )
                        )
                        return
                    else:
                        # Update existing user
                        user = User.objects.get(email=email)
                        user.set_password(password)
                        user.is_superuser = True
                        user.is_active = True
                        user.first_name = first_name
                        user.last_name = last_name
                        user.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✅ Updated existing superuser: {email}'
                            )
                        )
                else:
                    # Create new superuser
                    user = User.objects.create_superuser(
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Created new superuser: {email}'
                        )
                    )

                # Verify the user
                self.stdout.write(f"User details:")
                self.stdout.write(f"  Email: {user.email}")
                self.stdout.write(f"  Name: {user.first_name} {user.last_name}")
                self.stdout.write(f"  Is superuser: {user.is_superuser}")
                self.stdout.write(f"  Is active: {user.is_active}")

                # Test authentication
                from django.contrib.auth import authenticate
                auth_user = authenticate(email=email, password=password)
                if auth_user:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Password authentication test passed')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('❌ Password authentication test failed')
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating superuser: {str(e)}')
            )
            raise

        self.stdout.write(
            self.style.SUCCESS(
                '\n🎉 Test superuser setup complete!\n'
                f'You can now login with:\n'
                f'  Email: {email}\n'
                f'  Password: {password}\n'
            )
        )
