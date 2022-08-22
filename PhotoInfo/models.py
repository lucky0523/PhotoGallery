import logging
from django.db import models

from PhotoGallery.common import Static

LOG_TAG = '[PhotoInfo.models]'
logging.basicConfig(level=Static.LOG_LEVEL, format='%(asctime)s - %(name)s %(levelname)s - %(message)s')
logger = logging.getLogger(LOG_TAG)


class PhotoInfo(models.Model):
    vendor= models.CharField(max_length=100, default="", null=True, blank=True)
    device = models.CharField(max_length=100, default="", null=True, blank=True)

    def __str__(self):
        return 'Photo info:\r\nVendor:{}\r\nDevice:{}\r\n' \
            .format(self.vendor,
                    self.device)
