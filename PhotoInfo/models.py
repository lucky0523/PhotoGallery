import logging
import exifread
from datetime import datetime
from django.db import models

from PhotoGallery.common import Static, utils

LOG_TAG = '[PhotoInfo.models]'
logging.basicConfig(level=Static.LOG_LEVEL, format='%(asctime)s - %(name)s %(levelname)s - %(message)s')
logger = logging.getLogger(LOG_TAG)


class PhotoInfo(models.Model):
    path = models.CharField(max_length=200, default="", null=True, blank=True)
    thumbnail_path = models.CharField(max_length=200, default="", null=True, blank=True)
    vendor = models.CharField(max_length=100, default="", null=True, blank=True)
    device = models.CharField(max_length=100, default="", null=True, blank=True)
    shooting_time = models.DateTimeField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    length = models.IntegerField(null=True, blank=True)
    latitude = models.CharField(max_length=100, default="", null=True, blank=True)
    longitude = models.CharField(max_length=100, default="", null=True, blank=True)
    file_format = models.CharField(max_length=10, default="", null=True, blank=True)

    def __str__(self):
        return 'Photo info:\r\nVendor:{}\r\nDevice:{}\r\n' \
            .format(self.vendor,
                    self.device)

    def resolving(self):
        image_content = open(self.path, 'rb')
        self.file_format = self.path.split('.')[-1]

        tags = exifread.process_file(image_content)
        raw_time = tags['EXIF DateTimeOriginal'].printable.split(' ')
        raw_time[0] = raw_time[0].replace(':', '-')
        self.shooting_time = ' '.join(raw_time)
        self.vendor = tags['Image Make'].printable
        self.device = tags['Image Model'].printable
        self.width = int(tags['EXIF ExifImageWidth'].printable)
        self.length = int(tags['EXIF ExifImageLength'].printable)
        self.latitude = tags["GPS GPSLatitude"].printable[1:-1]
        self.longitude = tags["GPS GPSLongitude"].printable[1:-1]
        image_content.close()

        formatted_name = '.'.join(
            [self.vendor, self.device, self.shooting_time, self.file_format]) \
            .replace('-', '').replace(':', '').replace(' ', '').replace('*', '').replace('\\', '') \
            .replace('/', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')
        date = datetime.strptime(self.shooting_time, "%Y-%m-%d %H:%M:%S")
        self.path = utils.move_file(self.path, Static.PATH_SORTED_RAW_PHOTOS + str(date.year) + '/', formatted_name)
        self.thumbnail_path = utils.make_square_thumbnail(self.path, 240,
                                                          Static.PATH_SORTED_THUMBNAIL_PHOTOS + str(date.year) + '/',
                                                          formatted_name)
        self.save()
