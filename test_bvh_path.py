"""
Test if BVH path is correct
"""
from pathlib import Path
from django.conf import settings
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mocapnet_ui.settings')
django.setup()

bvh_root = Path(settings.HUMANBODY_ROOT) / 'data' / 'animations' / 'bvh'
print(f"BVH root: {bvh_root}")
print(f"Exists: {bvh_root.exists()}")
print(f"Is dir: {bvh_root.is_dir()}")

if bvh_root.is_dir():
    print("\nCategories:")
    for cat_dir in sorted(bvh_root.iterdir()):
        if cat_dir.is_dir():
            bvh_count = len(list(cat_dir.glob('*.bvh')))
            print(f"  {cat_dir.name}: {bvh_count} BVH files")
