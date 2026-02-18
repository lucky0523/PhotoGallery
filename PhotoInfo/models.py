import logging
import os
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
    path = models.TextField(default="", null=True, blank=True)
    thumbnail_path = models.TextField(default="", null=True, blank=True)
    show_path = models.TextField(default="", null=True, blank=True)
    vendor = models.CharField(max_length=100, default="", null=True, blank=True)
    device = models.CharField(max_length=100, default="", null=True, blank=True) # 设备认证名
    device_name = models.CharField(max_length=100, default="", null=True, blank=True) # 设备宣传名
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
    country = models.CharField(max_length=100, default="", null=True, blank=True)
    province = models.CharField(max_length=100, default="", null=True, blank=True)
    city = models.CharField(max_length=100, default="", null=True, blank=True)
    district = models.CharField(max_length=100, default="", null=True, blank=True)
    file_format = models.CharField(max_length=10, default="", null=True, blank=True)
    is_film = models.BooleanField(default=False)
    film_model = models.CharField(max_length=30, default="", null=True, blank=True)
    formatted_name = models.CharField(max_length=200, default="", null=True, blank=True)
    repeated = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repeated = False

    def __str__(self):
        return 'Photo info:\r\nVendor:{}\r\nDevice:{}\r\nPath:{}\r\n' \
            .format(self.vendor, self.device, self.path)

    def resolving(self, need_to_save_to_db=True, need_to_get_gps=True):
        logger.info(f'Process photo: {self.path}')
        if self.is_film:
            self.resolving_film(need_to_save_to_db)
        else:
            self.resolving_digital(need_to_save_to_db, need_to_get_gps)

    def resolving_digital(self, need_to_save_to_db=True, need_to_get_gps=True):
        raw_path = self.path
        logger.info('Process photo: {}'.format(raw_path))
        image_content = open(raw_path, 'rb')
        base_name, file_format_with_dot = os.path.splitext(raw_path)
        self.file_format = file_format_with_dot[1:]
        tags = exifread.process_file(image_content)
        image_content.close()
        # logger.info('EXIF tags: ' + str(tags))

        if 'Image Make' in tags:
            self.vendor = tags['Image Make'].printable
        if 'Image Model' in tags:
            self.device = tags['Image Model'].printable
        if 'EXIF Tag 0x9A00' in tags:
            self.device_name = tags['EXIF Tag 0x9A00'].printable
        
        # 先尝试DateTimeOriginal，若不存在则尝试Image DateTime，若都不存在则使用文件修改时间
        if 'EXIF DateTimeOriginal' in tags:
            raw_time = tags['EXIF DateTimeOriginal'].printable.split(' ')
            raw_time[0] = raw_time[0].replace(':', '-')
            self.shooting_time = ' '.join(raw_time)
        elif 'Image DateTime' in tags:
            raw_time = tags['Image DateTime'].printable.split(' ')
            raw_time[0] = raw_time[0].replace(':', '-')
            self.shooting_time = ' '.join(raw_time)
        else:
            file_mtime = os.path.getmtime(self.path)
            self.shooting_time = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d %H:%M:%S')
            logger.warning(f'No shooting time found in EXIF tags: {tags}, use file modify time instead: {self.shooting_time}')
        
        if 'EXIF ExposureTime' in tags:
            self.expo_time = tags['EXIF ExposureTime'].printable
        else:
            self.expo_time = -1
        if 'EXIF ISOSpeedRatings' in tags:
            self.iso = tags['EXIF ISOSpeedRatings'].printable
        else:
            self.iso = -1
        if 'EXIF FNumber' in tags:
            f_number_strs = tags['EXIF FNumber'].printable.split('/')
            if f_number_strs.__len__() > 1:
                self.f_number = int(f_number_strs[0]) / int(f_number_strs[1])
            else:
                self.f_number = float(f_number_strs[0])
        else:
            self.f_number = -1
        if 'EXIF FocalLengthIn35mmFilm' in tags:
            self.equivalent_focal_length = int(tags['EXIF FocalLengthIn35mmFilm'].printable)
        elif 'EXIF FocalLength' in tags:
            self.equivalent_focal_length = int(tags['EXIF FocalLength'].printable)
        if 'EXIF ExifImageWidth' in tags and 'EXIF ExifImageLength' in tags:
            self.width = int(tags['EXIF ExifImageWidth'].printable)
            self.length = int(tags['EXIF ExifImageLength'].printable)

        if need_to_get_gps:
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
                self.country, self.province, self.city, self.district = utils.decode_address_from_gps(self.latitude, self.longitude)

        if self.vendor !='' and self.device !='':
            self.formatted_name = '.'.join(
                [self.vendor, self.device, self.shooting_time, self.file_format]) \
                .replace('-', '').replace(':', '').replace(' ', '').replace('*', '').replace('\\', '') \
                .replace('/', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')
        else:
            #exif信息不完整时，formatted_name使用原文件名
            self.formatted_name = raw_path.split('/')[-1]
            logger.warning(f'Exif info not complete, use original filename instead: {self.formatted_name}')

        if need_to_save_to_db:
            date = datetime.strptime(self.shooting_time, "%Y-%m-%d %H:%M:%S")
            # 先保存数据库，再移动文件；否则若保存失败，文件又被移动，不好处理
            self.save()
            try:
                self.path = os.path.relpath(utils.move_file(raw_path, Static.PATH_SORTED_RAW_DIGITAL_PHOTOS() + str(date.year) + '/',
                                            self.formatted_name))
                self.thumbnail_path = os.path.relpath(utils.make_square_thumbnail(self.path, Static.SIZE_THUMBNAIL,
                                                                    Static.PATH_SORTED_THUMBNAIL_PHOTOS() + str(date.year) + '/',
                                                                    self.formatted_name))
                self.show_path = os.path.relpath(utils.make_show_image(self.path, Static.SIZE_SHOW_MAX_SIDE,
                                                        Static.PATH_SORTED_SHOW_PHOTOS() + str(date.year) + '/',
                                                        self.formatted_name))
                self.save()
            except Exception as e:
                logging.error(f"Error moving file: {e}, move to raw path: {raw_path}")
                # 若移动文件失败，删除数据库记录，文件也会被移动到原始位置，缩略图和显示图也会被删除
                self.path = os.path.relpath(utils.move_file(self.path, raw_path))
                if os.path.isfile(self.thumbnail_path):
                    os.remove(self.thumbnail_path)
                if os.path.isfile(self.show_path):
                    os.remove(self.show_path)
                self.delete()

    def resolving_film(self, need_to_save_to_db=True):
        self.file_format = self.path.split('.')[-1]
        self.is_film = True
        self.order_id = int(time.time() * 1000)
        self.formatted_name = str(self.order_id)


        if need_to_save_to_db:
            self.save()
            try:
                self.path = os.path.relpath(utils.move_file(self.path, Static.PATH_SORTED_RAW_FILMS(),
                                            self.formatted_name + '.' + self.file_format))
                self.thumbnail_path = os.path.relpath(utils.make_square_thumbnail(self.path, Static.SIZE_THUMBNAIL,
                                                                Static.PATH_SORTED_THUMBNAIL_PHOTOS() + Static.KEY_FILMS + '/',
                                                                self.formatted_name + Static.EXTS_THUMBNAIL))
                self.show_path = os.path.relpath(utils.make_show_image(self.path, Static.SIZE_SHOW_MAX_SIDE,
                                                    Static.PATH_SORTED_SHOW_PHOTOS() + Static.KEY_FILMS + '/',
                                                    self.formatted_name + Static.EXTS_THUMBNAIL))
                self.save()
            except Exception as e:
                logging.error(f"Error moving file: {e}, move to raw path: {raw_path}")
                # 若移动文件失败，删除数据库记录，文件也会被移动到原始位置，缩略图和显示图也会被删除
                self.path = os.path.relpath(utils.move_file(self.path, raw_path))
                if os.path.isfile(self.thumbnail_path):
                    os.remove(self.thumbnail_path)
                if os.path.isfile(self.show_path):
                    os.remove(self.show_path)
                self.delete()

    def set_order(self, order):
        self.order_id = order
        self.save()

    def set_position(self, longitude, latitude):
        self.longitude = float(longitude)
        self.latitude = float(latitude)
        self.country, self.province, self.city, self.district = utils.decode_address_from_gps(self.latitude, self.longitude)
        self.save()

    # 胶卷型号
    def set_film_model(self, model):
        self.film_model = model
        self.save()

    # test
    def read_exif(self):
        image_content = open(self.path, 'rb')
        tags = exifread.process_file(image_content)
        print(tags)
        print(int(tags['EXIF FocalLengthIn35mmFilm'].printable))
