"""fast_data_hub URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from fast_data_hub import views
from django_otp.admin import OTPAdminSite

urlpatterns = [
    path('', views.index, name='index'),
    path('models/', views.models, name='models'),
    path('pipelines/', views.pipelines, name='pipelines'),
    path('data/', views.data, name='data'),
    path('download/<str:item_id>/', views.download, name='download'),
    path('api/items/get/<str:item_id>/', views.api_get_item_files),
    path('api/pipelines/get/<str:item_id>/', views.api_get_pipeline_text, name='api_get_pipeline'),
    path('api/list/<str:tag>/', views.api_get_list),
    path('admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.THUMBNAIL_URL, document_root=settings.THUMBNAIL_ROOT) \
  + static(settings.UPLOAD_URL, document_root=settings.UPLOAD_ROOT)

if not settings.DEBUG:
    admin.site.__class__ = OTPAdminSite