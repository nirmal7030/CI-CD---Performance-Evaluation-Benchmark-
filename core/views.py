from django.http import JsonResponse, HttpResponse

def health(request):
    return JsonResponse({"status": "ok"})

def index(request):
    return HttpResponse("Django app is running.")
