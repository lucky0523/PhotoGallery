import json
import logging
import os
import random

from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q

from PhotoGallery.common import Static, utils
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
        dlist.sort(reverse=False)
        return render(request, 'navigation.html', context)


def resolving(request):
    for sub_path in os.scandir(Static.PATH_UNSORTED_PHOTOS):
        if os.path.isfile(sub_path):
            model = PhotoInfo(path=os.path.relpath(sub_path))
            model.resolving()
    plist = PhotoInfo.objects.all().order_by("-shooting_time")
    i = 0
    for p in plist:
        p.set_order(i)
        i = i + 1

    return HttpResponse('aaaaa')


def query_image(request):
    order_str = request.GET.get('order', -1)
    year_str = request.GET.get('year', -1)
    if year_str.isdigit() and int(year_str) > 1900:
        prev= PhotoInfo.objects.filter(shooting_time__year=year_str).order_by("order_id").filter(order_id__gt=order_str).first()
        nex = PhotoInfo.objects.filter(shooting_time__year=year_str).order_by("order_id").filter(order_id__lt=order_str).all().last()
    else:
        prev = PhotoInfo.objects.all().order_by("order_id").filter(order_id__gt=order_str).first()
        nex = PhotoInfo.objects.all().order_by("order_id").filter(order_id__lt=order_str).all().last()
    curr = PhotoInfo.objects.all().filter(order_id=order_str).first()
    p = curr
    if p is not None:
        view_dict = {
            'code': 200,
            'next': -1,
            'prev': -1,
            'order': p.order_id,
            'image': p.show_path[1:],
            'thumbnail': p.thumbnail_path[1:],
            'iso': p.iso,
            'f_number': p.f_number,
            'expo': p.expo_time,
            'focal_length': p.equivalent_focal_length,
            'city': p.city,
            'district': p.district,
            'time': p.shooting_time.strftime("%Y-%m-%d %H:%M:%S")}
        if p.device in Static.DEVICES_DICT:
            view_dict['device'] = Static.DEVICES_DICT[p.device]
        else:
            view_dict['device'] = p.device
        if nex is not None:
            view_dict['next'] = nex.order_id
        if prev is not None:
            view_dict['prev'] = prev.order_id
        print(view_dict)
    else:
        view_dict = {'code': 404, 'status': 'Not found!'}
    return HttpResponse(json.dumps(view_dict, sort_keys=True, indent=4, separators=(',', ': ')))


def query_list(request):
    randomly = request.GET.get('random', 0)
    year = request.GET.get('year', 1)
    view_list = []
    if int(randomly) > 0:
        plist = PhotoInfo.objects.all().order_by("-order_id")
    else:
        plist = PhotoInfo.objects.filter(shooting_time__year=year).order_by("-order_id")
    for p in plist:
        # p.read_exif()
        view_dict = {'order': p.order_id,
                     'image': p.show_path[1:],
                     'thumbnail': p.thumbnail_path[1:],
                     'iso': p.iso,
                     'f_number': p.f_number,
                     'expo': p.expo_time,
                     'focal_length': p.equivalent_focal_length,
                     'city': p.city,
                     'district': p.district,
                     'time': p.shooting_time.strftime("%Y-%m-%d %H:%M:%S")}
        if p.device in Static.DEVICES_DICT:
            view_dict['device'] = Static.DEVICES_DICT[p.device]
        else:
            view_dict['device'] = p.device
        view_list.append(view_dict)
    # if int(randomly) > 0:
        # random.shuffle(view_list)

    context = {'PageData': view_list}
    if request.method == 'POST':
        return render(request, 'gallery.html', context)
    else:
        return render(request, 'gallery.html', context)


def img_viewer(request):
    return render(request, 'image_viewer.html')


def reset(request):
    plist = PhotoInfo.objects.all()
    for p in plist:
        p.delete()
    utils.clear_dir(Static.PATH_SORTED_SHOW_PHOTOS)
    utils.clear_dir(Static.PATH_SORTED_THUMBNAIL_PHOTOS)
    utils.unsort_files(Static.PATH_SORTED_RAW_PHOTOS, Static.PATH_UNSORTED_PHOTOS)
    return HttpResponse('bbbb')
