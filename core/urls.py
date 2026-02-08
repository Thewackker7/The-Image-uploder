from django.urls import path
from . import views
from .health import health_check

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/drive/', views.upload_drive, name='upload_drive'),
    path('delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('health/', health_check, name='health_check'),
]
