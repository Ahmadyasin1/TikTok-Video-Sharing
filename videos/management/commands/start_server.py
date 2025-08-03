from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import sys
import signal
import os

class Command(BaseCommand):
    help = 'Start the development server with enhanced error handling'

    def add_arguments(self, parser):
        parser.add_argument(
            '--port',
            type=int,
            default=8000,
            help='Port to run the server on (default: 8000)',
        )
        parser.add_argument(
            '--host',
            type=str,
            default='127.0.0.1',
            help='Host to bind the server to (default: 127.0.0.1)',
        )

    def handle(self, *args, **options):
        port = options['port']
        host = options['host']
        
        self.stdout.write(self.style.SUCCESS('🚀 Starting VideoShare Platform Server'))
        self.stdout.write('=' * 50)
        
        # Run health check first
        self.stdout.write('Running health check...')
        try:
            call_command('health_check', '--fix')
            self.stdout.write(self.style.SUCCESS('✅ Health check completed'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️ Health check issues: {e}'))
        
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('🌐 SERVER INFORMATION'))
        self.stdout.write(f'• Server URL: http://{host}:{port}/')
        self.stdout.write(f'• Admin Dashboard: http://{host}:{port}/users/admin/database/')
        self.stdout.write(f'• Django Admin: http://{host}:{port}/admin/')
        self.stdout.write(f'• API Docs: See COMPLETE_API_USAGE_GUIDE.md')
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('🔑 ADMIN CREDENTIALS'))
        self.stdout.write('• Username: admin')
        self.stdout.write('• Password: admin123')
        self.stdout.write('\n' + '=' * 50)
        
        # Set up signal handler for graceful shutdown
        def signal_handler(sig, frame):
            self.stdout.write(self.style.SUCCESS('\n🛑 Shutting down server gracefully...'))
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            self.stdout.write(self.style.SUCCESS('✅ Server starting... Press Ctrl+C to stop'))
            self.stdout.write('')
            
            # Start the development server
            call_command('runserver', f'{host}:{port}', verbosity=1)
            
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('\n🛑 Server stopped by user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Server error: {e}'))
            
            # Provide troubleshooting tips
            self.stdout.write('\n' + '=' * 50)
            self.stdout.write(self.style.WARNING('🔧 TROUBLESHOOTING TIPS'))
            self.stdout.write('• Check if another process is using the port')
            self.stdout.write('• Ensure virtual environment is activated')
            self.stdout.write('• Run migrations: python manage.py migrate')
            self.stdout.write('• Check database connectivity')
            self.stdout.write('• Review error logs in logs/django.log')
            
            sys.exit(1)
