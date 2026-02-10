from django.http import HttpResponse




def index_page(request):
    return HttpResponse("Welcome to the Hospital Management System!")