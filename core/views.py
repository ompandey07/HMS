from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required




def index_page(request):
    return render(request, 'Base/index.html')




# #############################################################
# DASHBOARD VIEW
# #############################################################
@login_required(login_url='/accounts/login/')
def dashboard_page(request):
    """Dashboard page - requires login"""
    context = {
        'user': request.user,
        'hotel': getattr(request.user, 'hotel', None)
    }
    return render(request, 'dashboard/index.html', context)