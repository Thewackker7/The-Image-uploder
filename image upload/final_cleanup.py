import os
import django
import hashlib
import requests
from django.db.models import Count

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import ImagePost

def clean_gallery():
    # 1. Backfill missing hashes
    posts_to_hash = ImagePost.objects.filter(image_hash__isnull=True) | ImagePost.objects.filter(image_hash='')
    print(f"Backfilling {posts_to_hash.count()} posts...")
    for p in posts_to_hash:
        try:
            content = None
            if p.image_file:
                response = requests.get(p.image_file.url)
                if response.status_code == 200:
                    content = response.content
            elif p.image_url:
                content = p.image_url.encode()
            
            if content:
                p.image_hash = hashlib.sha256(content).hexdigest()
                p.save()
                print(f"Hashed post {p.id}")
        except Exception as e:
            print(f"Error hashing post {p.id}: {e}")

    # 2. Purge duplicates globally
    duplicate_hashes = ImagePost.objects.values('image_hash') \
        .annotate(count=Count('image_hash')) \
        .filter(count__gt=1) \
        .exclude(image_hash=None) \
        .exclude(image_hash='')

    print(f"Found {duplicate_hashes.count()} unique images with duplicates.")
    
    total_purged = 0
    for entry in duplicate_hashes:
        hash_val = entry['image_hash']
        all_with_hash = ImagePost.objects.filter(image_hash=hash_val).order_by('created_at')
        keep = all_with_hash.first()
        to_delete = all_with_hash.exclude(id=keep.id)
        cnt = to_delete.count()
        to_delete.delete()
        total_purged += cnt
        print(f"Hash {hash_val[:8]}: Kept {keep.id}, deleted {cnt} duplicates.")

    print(f"Final Cleanup Finished. Total purged: {total_purged}")

if __name__ == "__main__":
    clean_gallery()
