from django import forms
from .models import ImagePost

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImagePost
        fields = ['image_file']
