from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # App routes with proper prefixes
    # path('accounts/', include('accounts.routes')),
    # path('guests/', include('guests.routes')),
    # path('rooms/', include('rooms.routes')),
    # path('bookings/', include('bookings.routes')),
    # path('staff/', include('staff.routes')),
    # path('referrals/', include('referrals.routes')),
    # path('billing/', include('billing.routes')),
    # path('reports/', include('reports.routes')),
    path('', include('core.routes')),
]

# Static & Media files (development only)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
