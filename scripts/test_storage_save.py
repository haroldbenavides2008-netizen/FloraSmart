from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import django
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so Django settings module can be imported
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

name = default_storage.save('test_from_local2.txt', ContentFile(b'hello from local'))
print('saved_name=', name)
print('url=', default_storage.url(name))
