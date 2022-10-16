import logging
import time
import exifread
from datetime import datetime
from django.db import models

from PhotoGallery.common import Static, utils

LOG_TAG = '[PhotoInfo.models]'
logging.basicConfig(level=Static.LOG_LEVEL, format='%(asctime)s - %(name)s %(levelname)s - %(message)s')
logger = logging.getLogger(LOG_TAG)


class PhotoInfo(models.Model):
    id = models.AutoField(primary_key=True)
    order_id = models.IntegerField(null=True, blank=True)
    path = models.CharField(max_length=200, default="", null=True, blank=True)
    thumbnail_path = models.CharField(max_length=200, default="", null=True, blank=True)
    show_path = models.CharField(max_length=200, default="", null=True, blank=True)
    vendor = models.CharField(max_length=100, default="", null=True, blank=True)
    device = models.CharField(max_length=100, default="", null=True, blank=True)
    shooting_time = models.DateTimeField(null=True, blank=True)
    expo_time = models.CharField(max_length=100, default="", null=True, blank=True)
    iso = models.CharField(max_length=100, default="", null=True, blank=True)
    f_number = models.FloatField(null=True, blank=True)
    equivalent_focal_length = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    length = models.IntegerField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)
    province = models.CharField(max_length=100, default="", null=True, blank=True)
    city = models.CharField(max_length=100, default="", null=True, blank=True)
    district = models.CharField(max_length=100, default="", null=True, blank=True)
    file_format = models.CharField(max_length=10, default="", null=True, blank=True)
    is_film = models.BooleanField(default=False)
    film_model = models.CharField(max_length=30, default="", null=True, blank=True)

    def __str__(self):
        return 'Photo info:\r\nVendor:{}\r\nDevice:{}\r\n' \
            .format(self.vendor,
                    self.device)

    def resolving(self):
        image_content = open(self.path, 'rb')
        self.file_format = self.path.split('.')[-1]
        logger.info('Handle image: '+self.path)
        tags = exifread.process_file(image_content)
        image_content.close()
        if 'EXIF DateTimeOriginal' in tags:
            raw_time = tags['EXIF DateTimeOriginal'].printable.split(' ')
            raw_time[0] = raw_time[0].replace(':', '-')
            self.shooting_time = ' '.join(raw_time)
            self.vendor = tags['Image Make'].printable
            self.device = tags['Image Model'].printable
            self.expo_time = tags['EXIF ExposureTime'].printable
            self.iso = tags['EXIF ISOSpeedRatings'].printable
            f_number_strs = tags['EXIF FNumber'].printable.split('/')
            if f_number_strs.__len__() > 1:
                self.f_number = int(f_number_strs[0]) / int(f_number_strs[1])
            else:
                self.f_number = float(f_number_strs[0])
            if 'EXIF FocalLengthIn35mmFilm' in tags:
                self.equivalent_focal_length = int(tags['EXIF FocalLengthIn35mmFilm'].printable)
            elif 'EXIF FocalLength' in tags:
                self.equivalent_focal_length = int(tags['EXIF FocalLength'].printable)
            if 'EXIF ExifImageWidth' in tags and 'EXIF ExifImageLength' in tags:
                self.width = int(tags['EXIF ExifImageWidth'].printable)
                self.length = int(tags['EXIF ExifImageLength'].printable)
            try:
                latitude_str = tags["GPS GPSLatitude"].printable[1:-1]
                self.latitude = utils.sexagesimal2decimal(latitude_str)
            except:
                pass
            try:
                longitude_str = tags["GPS GPSLongitude"].printable[1:-1]
                self.longitude = utils.sexagesimal2decimal(longitude_str)
            except:
                pass
            try:
                altitude_strs = tags["GPS GPSAltitude"].printable.split('/')
                if altitude_strs.__len__() > 1:
                    self.altitude = float(altitude_strs[0]) / float(altitude_strs[1])
                else:
                    self.altitude = float(altitude_strs[0])
            except:
                pass
            if self.latitude is not None and self.longitude is not None:
                self.province, self.city, self.district = utils.decode_address_from_gps(self.latitude, self.longitude)

            formatted_name = '.'.join(
                [self.vendor, self.device, self.shooting_time, self.file_format]) \
                .replace('-', '').replace(':', '').replace(' ', '').replace('*', '').replace('\\', '') \
                .replace('/', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')
            date = datetime.strptime(self.shooting_time, "%Y-%m-%d %H:%M:%S")
            self.path = utils.move_file(self.path, Static.PATH_SORTED_RAW_PHOTOS + str(date.year) + '/', formatted_name)
            self.thumbnail_path = utils.make_square_thumbnail(self.path, Static.SIZE_THUMBNAIL,
                                                              Static.PATH_SORTED_THUMBNAIL_PHOTOS + str(date.year) + '/',
                                                              formatted_name)
            self.show_path = utils.make_show_image(self.path, Static.SIZE_SHOW_MAX_SIDE,
                                                   Static.PATH_SORTED_SHOW_PHOTOS + str(date.year) + '/',
                                                   formatted_name)
            self.save()

    def resolving_film(self):
        self.file_format = self.path.split('.')[-1]
        self.is_film = True
        self.order_id = int(time.time() * 1000)
        formatted_name = str(self.order_id)
        self.path = utils.move_file(self.path, Static.PATH_SORTED_RAW_FILMS, formatted_name + '.' + self.file_format)
        self.thumbnail_path = utils.make_square_thumbnail(self.path, Static.SIZE_THUMBNAIL,
                                                          Static.PATH_SORTED_THUMBNAIL_PHOTOS + Static.KEY_FILMS + '/',
                                                          formatted_name + '.jpg')
        self.show_path = utils.make_show_image(self.path, Static.SIZE_SHOW_MAX_SIDE,
                                               Static.PATH_SORTED_SHOW_PHOTOS + Static.KEY_FILMS + '/',
                                               formatted_name + '.jpg')
        self.save()

    def set_order(self, order):
        self.order_id = order
        self.save()

    def set_file_model(self, model):
        self.film_model = model
        self.save()

    def read_exif(self):
        image_content = open(self.path, 'rb')
        tags = exifread.process_file(image_content)
        print(tags)
        print(int(tags['EXIF FocalLengthIn35mmFilm'].printable))
        # print(utils.decode_address_from_gps(self.latitude, self.longitude))
