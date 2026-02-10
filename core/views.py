import os
import random
import json
import hashlib
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import ImagePost
from .forms import ImageUploadForm

from django.utils.timezone import make_aware
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
import io

ADJECTIVES = ['Neon', 'Cyber', 'Retro', 'Quantum', 'Pixel', 'Vapor', 'Holo', 'Glitch', 'Cosmic', 'Astro']
NOUNS = ['Panda', 'Fox', 'Surfer', 'Ninja', 'Samurai', 'Wizard', 'Driver', 'Ghost', 'Rider', 'Voyager']

def get_exif_date(file_obj):
    try:
        # Open the image properly
        image = Image.open(file_obj)
        exif = image._getexif()
        if not exif:
            return None
        
        for tag, value in exif.items():
            decoded = TAGS.get(tag, tag)
            if decoded == 'DateTimeOriginal':
                dt = datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                return make_aware(dt)
    except Exception:
        pass
    return None

def get_guest_name(request):
    if 'guest_name' not in request.session:
        # Generate a random name like "NeonPanda99"
        name = f"{random.choice(ADJECTIVES)}{random.choice(NOUNS)}{random.randint(10, 99)}"
        request.session['guest_name'] = name
    return request.session['guest_name']

def calculate_hash(file_obj):
    sha256_hash = hashlib.sha256()
    for chunk in file_obj.chunks():
        sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def home(request):
    try:
        guest_name = get_guest_name(request)
        form = ImageUploadForm()
        
        if request.method == 'POST':
            form = ImageUploadForm(request.POST, request.FILES)
            if form.is_valid():
                image_file = request.FILES.get('image_file')
                if image_file:
                    # Calculate hash for duplicate prevention
                    img_hash = calculate_hash(image_file)
                    image_file.seek(0)  # Reset pointer for Cloudinary
                    if ImagePost.objects.filter(image_hash=img_hash).exists():
                        messages.warning(request, "This photo has already been uploaded!")
                        return redirect('home')
                    
                    try:
                        post = form.save(commit=False)
                        post.guest_name = guest_name
                        post.image_hash = img_hash
                        
                        # Extract date taken
                        try:
                            image_file.seek(0)
                            post.taken_at = get_exif_date(image_file)
                            image_file.seek(0)
                        except Exception as e:
                            print(f"Failed to extract EXIF: {e}")
                        
                        post.save()
                        messages.success(request, "Memory saved successfully!")
                    except Exception as e:
                        print(f"Failed to save post: {e}")
                        messages.error(request, f"Failed to save memory: {str(e)}")
                return redirect('home')

        posts = ImagePost.objects.all()
        
        context = {
            'guest_name': guest_name,
            'form': form,
            'posts': posts,
            'google_api_key': os.environ.get('GOOGLE_API_KEY', ''),
            'google_app_id': os.environ.get('GOOGLE_APP_ID', ''), 
            'google_client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
        }
        return render(request, 'core/index.html', context)
    except Exception as e:
        import traceback
        from django.db import connection
        db_engine = connection.vendor
        print(f"ERROR in home view ({db_engine}): {e}")
        print(traceback.format_exc())
        # Return a simple error response instead of crashing
        from django.http import HttpResponse
        return HttpResponse(f"Server Error (DB: {db_engine}): {str(e)}<br><br>Check Render logs for details.", status=500)

import requests
from django.core.files.base import ContentFile

@csrf_exempt
def upload_drive(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_url = data.get('url')
            if not image_url:
                return JsonResponse({'status': 'error', 'message': 'No URL provided'}, status=400)
            
            # For Drive URLs, we download the content to ensure it's saved to Cloudinary
            try:
                # Use a proper User-Agent to avoid being blocked
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(image_url, headers=headers, timeout=10)
                response.raise_for_status()
                
                # Check if it's actually an image
                content_type = response.headers.get('Content-Type', '')
                if 'image' not in content_type:
                    # Some drive URLs might redirect or return HTML if not direct
                    return JsonResponse({'status': 'error', 'message': 'URL provided is not a direct image link'}, status=400)
                
                content = response.content
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Failed to download image: {str(e)}'}, status=400)

            img_hash = hashlib.sha256(content).hexdigest()
            if ImagePost.objects.filter(image_hash=img_hash).exists():
                return JsonResponse({'status': 'error', 'message': 'This photo has already been shared!'}, status=400)

            guest_name = get_guest_name(request)
            # Create the file name
            ext = content_type.split('/')[-1] if '/' in content_type else 'jpg'
            file_name = f"drive_{img_hash[:10]}.{ext}"
            
            post = ImagePost(
                guest_name=guest_name,
                image_hash=img_hash
            )

            # Extract date taken
            try:
                post.taken_at = get_exif_date(io.BytesIO(content))
            except Exception:
                pass

            # Save the content to the ImageField
            post.image_file.save(file_name, ContentFile(content), save=True)
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

@csrf_exempt
def delete_post(request, post_id):
    if not request.user.is_staff:
        messages.error(request, "Only admins can delete photos.")
        return redirect('home')
        
    post = get_object_or_404(ImagePost, id=post_id)
    post.delete()
    messages.success(request, "Photo deleted successfully.")
    return redirect('home')

