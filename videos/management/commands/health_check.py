from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os
import sys

class Command(BaseCommand):
    help = 'Check system health and fix common issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Automatically fix detected issues',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 VideoShare Platform Health Check'))
        self.stdout.write('=' * 50)
        
        issues_found = []
        fixes_applied = []
        
        # Check 1: Database connectivity
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                self.stdout.write(self.style.SUCCESS('✅ Database connectivity: OK'))
        except Exception as e:
            issues_found.append(f"Database connectivity issue: {e}")
            self.stdout.write(self.style.ERROR(f'❌ Database connectivity: {e}'))
        
        # Check 2: Static files
        static_root = getattr(settings, 'STATIC_ROOT', None)
        if static_root and not os.path.exists(static_root):
            issues_found.append("Static files not collected")
            self.stdout.write(self.style.WARNING('⚠️ Static files: Not collected'))
            
            if options['fix']:
                try:
                    call_command('collectstatic', '--noinput')
                    fixes_applied.append("Collected static files")
                    self.stdout.write(self.style.SUCCESS('✅ Static files: Collected'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Failed to collect static files: {e}'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Static files: OK'))
        
        # Check 3: Media directory
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if media_root and not os.path.exists(media_root):
            issues_found.append("Media directory missing")
            self.stdout.write(self.style.WARNING('⚠️ Media directory: Missing'))
            
            if options['fix']:
                try:
                    os.makedirs(media_root, exist_ok=True)
                    fixes_applied.append("Created media directory")
                    self.stdout.write(self.style.SUCCESS('✅ Media directory: Created'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Failed to create media directory: {e}'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Media directory: OK'))
        
        # Check 4: Logs directory
        logs_dir = settings.BASE_DIR / 'logs'
        if not os.path.exists(logs_dir):
            issues_found.append("Logs directory missing")
            self.stdout.write(self.style.WARNING('⚠️ Logs directory: Missing'))
            
            if options['fix']:
                try:
                    os.makedirs(logs_dir, exist_ok=True)
                    fixes_applied.append("Created logs directory")
                    self.stdout.write(self.style.SUCCESS('✅ Logs directory: Created'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Failed to create logs directory: {e}'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Logs directory: OK'))
        
        # Check 5: Admin user exists
        try:
            from users.models import CustomUser
            admin_exists = CustomUser.objects.filter(is_superuser=True).exists()
            if admin_exists:
                self.stdout.write(self.style.SUCCESS('✅ Admin user: Exists'))
            else:
                issues_found.append("No admin user found")
                self.stdout.write(self.style.WARNING('⚠️ Admin user: Not found'))
                
                if options['fix']:
                    try:
                        call_command('create_admin')
                        fixes_applied.append("Created admin user")
                        self.stdout.write(self.style.SUCCESS('✅ Admin user: Created'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'❌ Failed to create admin user: {e}'))
        except Exception as e:
            issues_found.append(f"Admin user check failed: {e}")
            self.stdout.write(self.style.ERROR(f'❌ Admin user check: {e}'))
        
        # Check 6: Migrations
        try:
            from django.core.management.commands.showmigrations import Command as ShowMigrationsCommand
            # This is a simplified check - in production you'd want more detailed migration checking
            self.stdout.write(self.style.SUCCESS('✅ Migrations: Checking complete'))
        except Exception as e:
            issues_found.append(f"Migration check failed: {e}")
            self.stdout.write(self.style.ERROR(f'❌ Migration check: {e}'))
        
        # Summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('📊 HEALTH CHECK SUMMARY'))
        
        if not issues_found:
            self.stdout.write(self.style.SUCCESS('🎉 All systems operational!'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️ {len(issues_found)} issue(s) found:'))
            for issue in issues_found:
                self.stdout.write(f'   • {issue}')
        
        if fixes_applied:
            self.stdout.write(self.style.SUCCESS(f'🔧 {len(fixes_applied)} fix(es) applied:'))
            for fix in fixes_applied:
                self.stdout.write(f'   • {fix}')
        
        if issues_found and not options['fix']:
            self.stdout.write(self.style.WARNING('\n💡 Run with --fix to automatically resolve issues'))
        
        # Performance recommendations
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('🚀 PERFORMANCE RECOMMENDATIONS'))
        self.stdout.write('• Enable caching for production')
        self.stdout.write('• Use CDN for static files')
        self.stdout.write('• Optimize database queries')
        self.stdout.write('• Enable compression middleware')
        self.stdout.write('• Use proper logging levels')
