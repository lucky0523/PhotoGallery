import json
import logging
import time

from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q

from PhotoGallery.common import Static

LOG_TAG = '[PhotoGallery.views] '
logging.basicConfig(level=Static.LOG_LEVEL, format='%(asctime)s - %(name)s %(levelname)s - %(message)s')
logger = logging.getLogger(LOG_TAG)


def nav(request):
    return render(request, 'navigation.html')
