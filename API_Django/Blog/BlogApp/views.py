from django.shortcuts import render
import requests
from django.shortcuts import render, redirect
from .forms import FoodForm,TravelForm,HealthyLifestyleForm,BeautyForm,PoliticsForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
def home_view(request):
    return render(request,'index.html')

form_map = {
    'travel': TravelForm,
    'food': FoodForm,
    'beauty': BeautyForm,
    'politics': PoliticsForm,
    'healthy_lifestyle': HealthyLifestyleForm,
}

# Flask API base URL
FLASK_API_URL = 'http://localhost:5000/api/forum'


def select_category(request):
    # Show categories as cards to select from
    categories = ['travel', 'food', 'beauty', 'politics', 'healthy_lifestyle']
    return render(request, 'forum/select_category.html', {'categories': categories})


def select_action(request, category):
    # Show action options (GET, POST, PUT, DELETE) for the selected category
    return render(request, 'forum/select_category.html', {'category': category})


def category_form(request, category, action, entry_id=None):
    form_class = form_map.get(category)
    if not form_class:
        return JsonResponse({'error': 'Invalid category'}, status=400)

    if action == 'get':
        # GET (list entries)
        res = requests.get(f'{FLASK_API_URL}/{category}')
        if res.status_code == 200:
            return render(request, 'forum/category_list.html', {
                'entries': res.json(),
                'category': category
            })
        return JsonResponse({'error': 'Failed to retrieve entries'}, status=400)

    if action == 'delete' and entry_id:
        # DELETE
        res = requests.delete(f'{FLASK_API_URL}/{category}/{entry_id}')
        if res.status_code == 200:
            return redirect('category_action', category=category, action='get')
        return JsonResponse({'error': 'Failed to delete entry'}, status=400)

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if action == 'post':
                res = requests.post(f'{FLASK_API_URL}/{category}', json=data)
            elif action == 'put' and entry_id:
                res = requests.put(f'{FLASK_API_URL}/{category}/{entry_id}', json=data)
            else:
                return JsonResponse({'error': 'Invalid action or missing ID for PUT'}, status=400)

            if res.status_code in [200, 201]:
                return redirect('category_action', category=category, action='get')
            return JsonResponse({'error': 'Failed to submit data to Flask'}, status=res.status_code)
    else:
        if action == 'put' and entry_id:
            # Prefill form for editing
            res = requests.get(f'{FLASK_API_URL}/{category}')
            if res.status_code == 200:
                entry = next((e for e in res.json() if e['id'] == entry_id), None)
                if entry:
                    form = form_class(initial=entry['data'])
                else:
                    return JsonResponse({'error': 'Entry not found'}, status=404)
            else:
                return JsonResponse({'error': 'Failed to fetch data from API'}, status=res.status_code)
        else:
            form = form_class()

    return render(request, 'forum/category_form.html', {
        'form': form,
        'category': category,
        'action': action,
        'entry_id': entry_id
    })