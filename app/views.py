from django.shortcuts import render

# Create your views here.
def home_page(request):
    return render(request, 'home.html', {
        'search_results_text': request.POST.get('search_query_text')
    })