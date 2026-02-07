from django.db import models
from cloudinary.models import CloudinaryField

class ImagePost(models.Model):
    guest_name = models.CharField(max_length=100)
    image_file = models.ImageField(upload_to='images/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    image_hash = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    taken_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.guest_name} - {self.created_at}"

    class Meta:
        ordering = ['-created_at']
