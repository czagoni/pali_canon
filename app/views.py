import os

from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse

from app.search import Search, create_index


# Create your views here.
def home_page(request):
    #create_index(settings.INDEX_DIR, settings.TEXT_DIR)
    return render(request, 'home.html')
    
def search(request):
    return JsonResponse(Search(settings.INDEX_DIR, settings.TEXT_DIR) \
                           .search(request.GET.get('search_query_text')))

def get_help_text(request):

    with open(os.path.join(settings.BASE_DIR, 'app/templates/help_text.html'), 'rt') as f:
        help_text = f.read()
    return JsonResponse({'help_text': help_text})                        