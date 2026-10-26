import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from django.test import Client

c = Client()
try:
    print("Sending GET /...")
    r = c.get('/')
    print("Status code:", r.status_code)
    print("Response length:", len(r.content))
except Exception as e:
    import traceback
    traceback.print_exc()
