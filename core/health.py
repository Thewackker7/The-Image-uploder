"""
Health check view for debugging Render deployment
"""
import os
from django.http import JsonResponse
from django.db import connection
from django.conf import settings

def health_check(request):
    """
    Simple health check endpoint to verify:
    - Django is running
    - Database connection works
    - Environment variables are set
    """
    status = {
        'django': 'OK',
        'database': 'UNKNOWN',
        'cloudinary': 'UNKNOWN',
        'debug': settings.DEBUG,
        'allowed_hosts': settings.ALLOWED_HOSTS,
    }
    
    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            status['database'] = 'OK'
    except Exception as e:
        status['database'] = f'ERROR: {str(e)[:100]}'
    
    # Check Cloudinary config
    try:
        from cloudinary import config as cloudinary_config
        cloud_name = cloudinary_config().cloud_name
        if cloud_name:
            status['cloudinary'] = 'OK'
        else:
            status['cloudinary'] = 'NOT CONFIGURED'
    except Exception as e:
        status['cloudinary'] = f'ERROR: {str(e)[:100]}'
    
    # Check migrations
    try:
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        status['pending_migrations'] = [str(migration) for migration, backwards in plan]
        status['migrations_synced'] = len(plan) == 0
    except Exception as e:
        status['pending_migrations'] = f'ERROR: {str(e)}'
    
    # Check environment variables (without exposing values)
    status['env_vars'] = {
        'DATABASE_URL': 'SET' if os.environ.get('DATABASE_URL') else 'NOT SET',
        'CLOUDINARY_URL': 'SET' if os.environ.get('CLOUDINARY_URL') else 'NOT SET',
        'SECRET_KEY': 'SET' if os.environ.get('SECRET_KEY') else 'NOT SET',
        'RENDER': 'SET' if os.environ.get('RENDER') else 'NOT SET',
    }
    
    return JsonResponse(status, json_dumps_params={'indent': 2})
