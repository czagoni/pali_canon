from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse

from app.search import Search, create_index

from django.contrib.staticfiles.storage import staticfiles_storage

# Create your views here.
def home_page(request):
    #create_index(settings.INDEX_DIR, settings.TEXT_DIR)
    return render(request, 'home.html')
    
def search(request):

    return JsonResponse(Search(settings.INDEX_DIR, settings.TEXT_DIR) \
                           .search(request.GET.get('search_query_text')))