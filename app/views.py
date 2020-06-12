from django.shortcuts import render
from app.search import Search, create_index
from django.conf import settings


# Create your views here.
def home_page(request):
    create_index(settings.INDEX_DIR, settings.TEXT_DIR)
    return render(request, 'home.html')


def results_page(request):

    results = Search(settings.INDEX_DIR, settings.TEXT_DIR) \
                    .search(request.POST.get('search_query_text'))

    return render(request, 'results.html', {
        'search_results': results
    })