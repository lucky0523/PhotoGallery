import logging
import os
import sys

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

_initialized = False
_PATH_SORTED_RAW_DIGITAL_PHOTOS = None
_PATH_SORTED_RAW_FILMS = None
_PATH_SORTED_SHOW_PHOTOS = None
_PATH_SORTED_THUMBNAIL_PHOTOS = None
_PATH_UPLOADED_DIGITAL_PHOTOS = None
_PATH_UPLOADED_THUMBNAIL = None
_PATH_UPLOADED_FILMS = None


def _init_paths():
    global _initialized
    global _PATH_SORTED_RAW_DIGITAL_PHOTOS
    global _PATH_SORTED_SHOW_PHOTOS
    global _PATH_SORTED_THUMBNAIL_PHOTOS
    global _PATH_SORTED_RAW_FILMS
    global _PATH_UPLOADED_DIGITAL_PHOTOS
    global _PATH_UPLOADED_THUMBNAIL
    global _PATH_UPLOADED_FILMS
    
    if _initialized:
        return
    
    from django.conf import settings
    _PATH_SORTED_RAW_DIGITAL_PHOTOS = os.path.join(settings.MEDIA_ROOT, 'photos', 'raw_digital') + '/'
    _PATH_SORTED_SHOW_PHOTOS = os.path.join(settings.MEDIA_ROOT, 'photos', 'show') + '/'
    _PATH_SORTED_THUMBNAIL_PHOTOS = os.path.join(settings.MEDIA_ROOT, 'photos', 'thumbnail') + '/'
    _PATH_SORTED_RAW_FILMS = os.path.join(settings.MEDIA_ROOT, 'photos', 'raw_films') + '/'
    _PATH_UPLOADED_DIGITAL_PHOTOS = os.path.join(settings.MEDIA_ROOT, 'uploaded', 'digital_photos') + '/'
    _PATH_UPLOADED_THUMBNAIL = os.path.join(settings.MEDIA_ROOT, 'uploaded', 'thumbnail') + '/'
    _PATH_UPLOADED_FILMS = os.path.join(settings.MEDIA_ROOT, 'uploaded', 'films') + '/'
    
    _initialized = True


class _ModuleProxy:
    def __getattr__(self, name):
        if name == 'PATH_SORTED_RAW_DIGITAL_PHOTOS':
            _init_paths()
            return _PATH_SORTED_RAW_DIGITAL_PHOTOS
        elif name == 'PATH_SORTED_SHOW_PHOTOS':
            _init_paths()
            return _PATH_SORTED_SHOW_PHOTOS
        elif name == 'PATH_SORTED_THUMBNAIL_PHOTOS':
            _init_paths()
            return _PATH_SORTED_THUMBNAIL_PHOTOS
        elif name == 'PATH_SORTED_RAW_FILMS':
            _init_paths()
            return _PATH_SORTED_RAW_FILMS
        elif name == 'PATH_UPLOADED_DIGITAL_PHOTOS':
            _init_paths()
            return _PATH_UPLOADED_DIGITAL_PHOTOS
        elif name == 'PATH_UPLOADED_THUMBNAIL':
            _init_paths()
            return _PATH_UPLOADED_THUMBNAIL
        elif name == 'PATH_UPLOADED_FILMS':
            _init_paths()
            return _PATH_UPLOADED_FILMS
        else:
            return globals()[name]


def ensure_path_directories_exist():
    """
    自动创建所有以 PATH_ 开头的路径目录
    """
    _init_paths()
    path_attrs = [
        'PATH_SORTED_RAW_DIGITAL_PHOTOS',
        'PATH_SORTED_SHOW_PHOTOS',
        'PATH_SORTED_THUMBNAIL_PHOTOS',
        'PATH_SORTED_RAW_FILMS',
        'PATH_UPLOADED_DIGITAL_PHOTOS',
        'PATH_UPLOADED_THUMBNAIL',
        'PATH_UPLOADED_FILMS',
    ]
    for attr_name in path_attrs:
        try:
            full_path = getattr(_proxy, attr_name)
            if isinstance(full_path, str) and full_path.strip():
                if not os.path.exists(full_path):
                    os.makedirs(full_path, exist_ok=True)
                    logging.info(f"Created directory: {full_path}")
                else:
                    logging.info(f"Directory already exists: {full_path}")
        except Exception as e:
            logging.warning(f"Failed to ensure directory for {attr_name}: {e}")


_proxy = _ModuleProxy()
sys.modules[__name__] = _proxy
