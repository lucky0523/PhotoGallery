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
    for sub_path in os.scandir(Static.PATH_SORTED_PHOTOS):
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
