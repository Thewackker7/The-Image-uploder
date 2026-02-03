import os
import django
from django.db.models import Count

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import ImagePost

def purge_duplicates():
    # Find all hashes that appear more than once
    duplicate_hashes = ImagePost.objects.values('image_hash') \
        .annotate(count=Count('image_hash')) \
        .filter(count__gt=1) \
        .exclude(image_hash=None) \
        .exclude(image_hash='')

    print(f"Found {duplicate_hashes.count()} unique images that have duplicates.")
    
    total_purged = 0
    for entry in duplicate_hashes:
        hash_val = entry['image_hash']
        # Get all posts with this hash, ordered by date
        all_with_hash = ImagePost.objects.filter(image_hash=hash_val).order_by('created_at')
        
        # Keep the oldest one
        keep = all_with_hash.first()
        # Delete the rest
        to_delete = all_with_hash.exclude(id=keep.id)
        count = to_delete.count()
        to_delete.delete()
        
        total_purged += count
        print(f"Hash {hash_val[:10]}...: Kept post {keep.id} (by {keep.guest_name}), deleted {count} duplicates.")

    print(f"Successfully purged {total_purged} total duplicate posts.")

if __name__ == "__main__":
    purge_duplicates()
