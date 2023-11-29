"""PhotoGallery URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, re_path
from django.views.static import serve
from django.conf import settings

from PhotoGallery import views

urlpatterns = [
    re_path(r'^$', views.nav),
    path('re/', views.resolving),
    path('editor', views.editor),
    path('uploader', views.uploader),

    path('query_list', views.query_list),
    path('query_image', views.query_image),
    path('reset', views.reset),
    path('imgviewer', views.img_viewer),
    path('edit_photo', views.edit_photo),
    path('get_all_films', views.get_all_films),
    path('tencent9176013635572033544.txt/', views.wx_verify),
    re_path('dynamic/photos/sorted/show/(?P<path>.*)', serve, {'document_root': settings.SHOW_IMAGE_ROOT}),
    re_path('dynamic/photos/sorted/thumbnail/(?P<path>.*)', serve, {'document_root': settings.THUMBNAIL_IMAGE_ROOT}),
    re_path('dynamic/uploaded/(?P<path>.*)', serve, {'document_root': settings.UPLOADED_IMAGE_ROOT}),
]
