from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Only run in production (on Render) to avoid local dev overhead
        import os
        if os.environ.get('RENDER'):
            from django.core.management import call_command
            import threading

            def run_create_admin():
                try:
                    call_command('create_admin')
                except Exception as e:
                    print(f"Error creating admin on startup: {e}")

            # Run in a background thread to not block the main process startup
            threading.Thread(target=run_create_admin, daemon=True).start()
