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

ADJECTIVES = ['Neon', 'Cyber', 'Retro', 'Quantum', 'Pixel', 'Vapor', 'Holo', 'Glitch', 'Cosmic', 'Astro']
NOUNS = ['Panda', 'Fox', 'Surfer', 'Ninja', 'Samurai', 'Wizard', 'Driver', 'Ghost', 'Rider', 'Voyager']

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
                
                post = form.save(commit=False)
                post.guest_name = guest_name
                post.image_hash = img_hash
                post.save()
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

@csrf_exempt
def upload_drive(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_url = data.get('url')
            if not image_url:
                return JsonResponse({'status': 'error', 'message': 'No URL provided'}, status=400)
            
            # For Drive URLs, we use the URL as a hash for now as fetching content might be complex
            # and require auth tokens in headers.
            img_hash = hashlib.sha256(image_url.encode()).hexdigest()
            if ImagePost.objects.filter(image_hash=img_hash).exists():
                return JsonResponse({'status': 'error', 'message': 'This photo has already been shared!'}, status=400)

            guest_name = get_guest_name(request)
            ImagePost.objects.create(
                guest_name=guest_name,
                image_url=image_url,
                image_hash=img_hash
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

def delete_post(request, post_id):
    post = get_object_or_404(ImagePost, id=post_id)
    # Only allow the owner to delete
    if post.guest_name == request.session.get('guest_name'):
        post.delete()
        messages.success(request, "Photo deleted successfully.")
    else:
        messages.error(request, "You can only delete your own photos.")
    return redirect('home')
