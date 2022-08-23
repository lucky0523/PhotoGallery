import json
import logging
import os
import time

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
    for sub_path in os.scandir(Static.PATH_PHOTOS):
        if os.path.isdir(sub_path):
            dlist.append(os.path.basename(sub_path))
    context = {'PhotoDictionary': dlist}
    return render(request, 'navigation.html', context)


def resolving(request):
    for sub_path in os.scandir(Static.PATH_PHOTOS):
        if os.path.isdir(sub_path):
            for f in os.scandir(sub_path):
                if os.path.isfile(f):
                    model = PhotoInfo(path=os.path.relpath(f))
                    model.resolving()
                    model.save()
            break
    return HttpResponse('aaaaa')
