from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("core.urls")),
    path('ebooking/',include("ebooking.urls")),
    path('carbooking/',include("carbooking.urls")),
    path('dttdc_admin/',include('dttdc_admin.urls')),
    path('dttdc_car_admin/',include('dttdc_car_admin.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
handler404 = "dttdc_beta_v1.views.custom_404"