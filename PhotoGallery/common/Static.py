import logging
import os
import sys

LANGUAGE = 'zh'

LOG_LEVEL = logging.INFO

KEY_API_VERSION = 'api_version'
API_VERSION = '0.1'

SIZE_THUMBNAIL = 500
SIZE_SHOW_MAX_SIDE = 2400
SUFFIX_THUMBNAIL = '.jpg'

KEY_FILMS = 'films'
EARLIER_YEAR = 2019

KEY_BAIDUMAP_SERVER_SECRET_AK = 'tiH1vWxXhdEhvwWcNkv9wlh42MDFKomR'
KEY_BAIDUMAP_WEB_SECRET_AK = 'TSuBY5iecr0Qjq8jvTJrghaLchcEsXMG'
KEY_LOCATIONIQ_API_KEY = 'pk.01dc375f25ac297af2c84a48532a291c'
KEY_BIGDATACLOUD_API_KEY = 'bdc_9309edc9429241c382c2deac7943d59c'

KEY_FILM = 'film'
KEY_DIGITAL = 'digital'

DEVICES_DICT = {
    'M2007J1SC': 'Mi10 Ultra',
    '2304FPN6DG': 'Mi13 Ultra',
    'SM-G9650': 'Samsung S9',
    'FC220': 'Dji Mavic Pro',
}

PIC_EXTS = ('.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.raw', '.cr2', '.nef', '.arw', '.heic')

_initialized = False
_PATH_UNSORTED_PHOTOS = None
_PATH_SORTED_RAW_PHOTOS = None
_PATH_SORTED_SHOW_PHOTOS = None
_PATH_SORTED_THUMBNAIL_PHOTOS = None
_PATH_UNSORTED_FILMS = None
_PATH_SORTED_RAW_FILMS = None
_PATH_UPLOADED = None
_PATH_UPLOADED_TEMP = None
_PATH_UPLOADED_FILMS = None


def _init_paths():
    global _initialized
    global _PATH_UNSORTED_PHOTOS
    global _PATH_SORTED_RAW_PHOTOS
    global _PATH_SORTED_SHOW_PHOTOS
    global _PATH_SORTED_THUMBNAIL_PHOTOS
    global _PATH_UNSORTED_FILMS
    global _PATH_SORTED_RAW_FILMS
    global _PATH_UPLOADED
    global _PATH_UPLOADED_TEMP
    global _PATH_UPLOADED_FILMS
    
    if _initialized:
        return
    
    from django.conf import settings
    _PATH_UNSORTED_PHOTOS = os.path.join(settings.MEDIA_ROOT, 'photos', 'unsorted') + '/'
    _PATH_SORTED_RAW_PHOTOS = os.path.join(settings.MEDIA_ROOT, 'photos', 'sorted', 'raw') + '/'
    _PATH_SORTED_SHOW_PHOTOS = os.path.join(settings.MEDIA_ROOT, 'photos', 'sorted', 'show') + '/'
    _PATH_SORTED_THUMBNAIL_PHOTOS = os.path.join(settings.MEDIA_ROOT, 'photos', 'sorted', 'thumbnail') + '/'
    _PATH_UNSORTED_FILMS = os.path.join(settings.MEDIA_ROOT, 'photos', 'unsorted_films') + '/'
    _PATH_SORTED_RAW_FILMS = os.path.join(settings.MEDIA_ROOT, 'photos', 'sorted', 'raw_films') + '/'
    _PATH_UPLOADED = os.path.join(settings.MEDIA_ROOT, 'uploaded') + '/'
    _PATH_UPLOADED_TEMP = os.path.join(settings.MEDIA_ROOT, 'uploaded', 'temp') + '/'
    _PATH_UPLOADED_FILMS = os.path.join(settings.MEDIA_ROOT, 'uploaded', 'films') + '/'
    
    _initialized = True


class _ModuleProxy:
    def __getattr__(self, name):
        if name == 'PATH_UNSORTED_PHOTOS':
            _init_paths()
            return _PATH_UNSORTED_PHOTOS
        elif name == 'PATH_SORTED_RAW_PHOTOS':
            _init_paths()
            return _PATH_SORTED_RAW_PHOTOS
        elif name == 'PATH_SORTED_SHOW_PHOTOS':
            _init_paths()
            return _PATH_SORTED_SHOW_PHOTOS
        elif name == 'PATH_SORTED_THUMBNAIL_PHOTOS':
            _init_paths()
            return _PATH_SORTED_THUMBNAIL_PHOTOS
        elif name == 'PATH_UNSORTED_FILMS':
            _init_paths()
            return _PATH_UNSORTED_FILMS
        elif name == 'PATH_SORTED_RAW_FILMS':
            _init_paths()
            return _PATH_SORTED_RAW_FILMS
        elif name == 'PATH_UPLOADED':
            _init_paths()
            return _PATH_UPLOADED
        elif name == 'PATH_UPLOADED_TEMP':
            _init_paths()
            return _PATH_UPLOADED_TEMP
        elif name == 'PATH_UPLOADED_FILMS':
            _init_paths()
            return _PATH_UPLOADED_FILMS
        elif name == 'ensure_path_directories_exist':
            return ensure_path_directories_exist
        else:
            return globals()[name]


def ensure_path_directories_exist():
    """
    自动创建所有以 PATH_ 开头的路径目录
    """
    _init_paths()
    path_attrs = [
        'PATH_UNSORTED_PHOTOS',
        'PATH_SORTED_RAW_PHOTOS',
        'PATH_SORTED_SHOW_PHOTOS',
        'PATH_SORTED_THUMBNAIL_PHOTOS',
        'PATH_UNSORTED_FILMS',
        'PATH_SORTED_RAW_FILMS',
        'PATH_UPLOADED',
        'PATH_UPLOADED_TEMP',
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
