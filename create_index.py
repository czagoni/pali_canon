from app.search import create_index
from django.conf import settings

create_index(settings.INDEX_DIR, settings.TEXT_DIR)