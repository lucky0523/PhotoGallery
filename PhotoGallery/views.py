import json
import logging
import os
import random

from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q

from PhotoGallery.common import Static
from PhotoInfo.models import PhotoInfo

LOG_TAG = '[PhotoGallery.views] '
logging.basicConfig(level=Static.LOG_LEVEL, format='%(asctime)s - %(name)s %(levelname)s - %(message)s')
logger = logging.getLogger(LOG_TAG)


def nav(request):
    dlist = []
    if not os.path.exists(Static.PATH_SORTED_RAW_PHOTOS):
        return render(request, 'navigation.html')
    else:
        for sub_path in os.scandir(Static.PATH_SORTED_RAW_PHOTOS):
            if os.path.isdir(sub_path):
                dlist.append(os.path.basename(sub_path))
        context = {'PhotoDictionary': dlist}
        return render(request, 'navigation.html', context)


def resolving(request):
    for sub_path in os.scandir(Static.PATH_UNSORTED_PHOTOS):
        if os.path.isfile(sub_path):
            model = PhotoInfo(path=os.path.relpath(sub_path))
            model.resolving()

    return HttpResponse('aaaaa')


def query(request):
    randomly = request.GET.get('random', 0)
    year = request.GET.get('year', 1)
    vendor = request.GET.get('vendor', 1)
    view_list = []
    if int(randomly) > 0:
        plist = PhotoInfo.objects.all()
    else:
        plist = PhotoInfo.objects.filter(shooting_time__year=year)
    for p in plist:
        # p.read_exif()
        view_dict = {}
        view_dict['image'] = p.path[1:]
        view_dict['thumbnail'] = p.thumbnail_path[1:]
        view_dict['iso'] = p.iso
        view_dict['f_number'] = p.f_number
        view_dict['expo'] = p.expo_time
        view_dict['focal_length'] = p.equivalent_focal_length
        view_list.append(view_dict)
    if int(randomly) > 0:
        random.shuffle(view_list)

    context = {'PageData': view_list}
    if request.method == 'POST':
        return render(request, 'gallery.html', context)
    else:
        return render(request, 'gallery.html', context)


def img_viewer(request):
    return render(request, 'image_viewer.html')
