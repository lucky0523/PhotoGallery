import logging
import os
import sys
from django.conf import settings

LANGUAGE = 'zh'

LOG_LEVEL = logging.INFO

KEY_API_VERSION = 'api_version'
API_VERSION = '0.1'

SIZE_THUMBNAIL = 500
SIZE_SHOW_MAX_SIDE = 2400

KEY_FILMS = 'films'
EARLIER_YEAR = 2019

KEY_BAIDUMAP_SERVER_SECRET_AK = 'tiH1vWxXhdEhvwWcNkv9wlh42MDFKomR'
KEY_BAIDUMAP_WEB_SECRET_AK = 'TSuBY5iecr0Qjq8jvTJrghaLchcEsXMG'
KEY_LOCATIONIQ_API_KEY = 'pk.01dc375f25ac297af2c84a48532a291c'
KEY_BIGDATACLOUD_API_KEY = 'bdc_9309edc9429241c382c2deac7943d59c'

DEVICES_DICT = {
    'M2007J1SC': 'Mi10 Ultra',
    '2304FPN6DG': 'Mi13 Ultra',
    'SM-G9650': 'Samsung S9',
    'FC220': 'Dji Mavic Pro',
}

EXTS_THUMBNAIL = '.jpg'
EXTS_PIC = ('.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.raw', '.cr2', '.nef', '.arw', '.heic')


def PATH_SORTED_RAW_DIGITAL_PHOTOS():
    return os.path.join(settings.MEDIA_ROOT, 'photos', 'raw_digital') + '/'


def PATH_SORTED_RAW_FILMS():
    return os.path.join(settings.MEDIA_ROOT, 'photos', 'raw_films') + '/'


def PATH_SORTED_SHOW_PHOTOS():
    return os.path.join(settings.MEDIA_ROOT, 'photos', 'show') + '/'


def PATH_SORTED_THUMBNAIL_PHOTOS():
    return os.path.join(settings.MEDIA_ROOT, 'photos', 'thumbnail') + '/'


def PATH_UPLOADED_DIGITAL_PHOTOS():
    return os.path.join(settings.MEDIA_ROOT, 'uploaded', 'digital_photos') + '/'


def PATH_UPLOADED_THUMBNAIL():
    return os.path.join(settings.MEDIA_ROOT, 'uploaded', 'thumbnail') + '/'


def PATH_UPLOADED_FILMS():
    return os.path.join(settings.MEDIA_ROOT, 'uploaded', 'films') + '/'


def ensure_path_directories_exist():
    """
    自动创建所有以 PATH_ 开头的路径目录
    """
    import inspect
    current_module = sys.modules[__name__]
    path_funcs = []
    for name, obj in inspect.getmembers(current_module):
        if name.startswith('PATH_') and inspect.isfunction(obj):
            path_funcs.append(obj)
    
    for func in path_funcs:
        try:
            full_path = func()
            if isinstance(full_path, str) and full_path.strip():
                if not os.path.exists(full_path):
                    os.makedirs(full_path, exist_ok=True)
                    logging.info(f"Created directory: {full_path}")
                else:
                    logging.info(f"Directory already exists: {full_path}")
        except Exception as e:
            logging.warning(f"Failed to ensure directory: {e}")
