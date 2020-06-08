from django.shortcuts import render
from app.search import Search

# Create your views here.
def home_page(request):
    return render(request, 'home.html')


def results_page(request):

    results = Search().search(request.POST.get('search_query_text'))

    print(len(results))
    return render(request, 'results.html', {
        'search_results': results
    })