import os
import django
# import sys
# from pathlib import Path


# BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

# sys.path.append(str(BASE_DIR / "smartup"))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from tgbot.handlers.dispatcher import run_pooling

if __name__ == "__main__":
    run_pooling()