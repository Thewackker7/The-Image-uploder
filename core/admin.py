from django.contrib import admin
from django.utils.html import format_html
from .models import ImagePost

@admin.register(ImagePost)
class ImagePostAdmin(admin.ModelAdmin):
    list_display = ('guest_name', 'image_preview', 'created_at', 'taken_at')
    list_filter = ('created_at', 'guest_name')
    search_fields = ('guest_name',)
    readonly_fields = ('image_hash',)

    def image_preview(self, obj):
        if obj.image_file:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.image_file.url)
        elif obj.image_url:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.image_url)
        return "No Image"
    image_preview.short_description = 'Preview'

