import logging
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

LANGUAGE = 'zh'

LOG_LEVEL = logging.INFO

KEY_API_VERSION = 'api_version'
API_VERSION = '0.1'

PATH_UNSORTED_PHOTOS = str(BASE_DIR / 'data' / 'dynamic' / 'photos' / 'unsorted') + '/'
PATH_SORTED_RAW_PHOTOS = str(BASE_DIR / 'data' / 'dynamic' / 'photos' / 'sorted' / 'raw') + '/'
PATH_SORTED_SHOW_PHOTOS = str(BASE_DIR / 'data' / 'dynamic' / 'photos' / 'sorted' / 'show') + '/'
PATH_SORTED_THUMBNAIL_PHOTOS = str(BASE_DIR / 'data' / 'dynamic' / 'photos' / 'sorted' / 'thumbnail') + '/'
PATH_UNSORTED_FILMS = str(BASE_DIR / 'data' / 'dynamic' / 'photos' / 'unsorted_films') + '/'
PATH_SORTED_RAW_FILMS = str(BASE_DIR / 'data' / 'dynamic' / 'photos' / 'sorted' / 'raw_films') + '/'
PATH_UPLOADED = str(BASE_DIR / 'data' / 'dynamic' / 'uploaded') + '/'
PATH_UPLOADED_TEMP = str(BASE_DIR / 'data' / 'dynamic' / 'uploaded' / 'temp') + '/'
PATH_UPLOADED_FILMS = str(BASE_DIR / 'data' / 'dynamic' / 'uploaded' / 'films') + '/'

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


def ensure_path_directories_exist():
    """
    自动创建所有以 PATH_ 开头的路径目录
    """
    import sys
    current_module = sys.modules[__name__]
    for attr_name in dir(current_module):
        if attr_name.startswith('PATH_'):
            path = getattr(current_module, attr_name)
            if isinstance(path, str) and path.strip():
                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)
                    logging.info(f"Created directory: {path}")
                else:
                    logging.info(f"Directory already exists: {path}")
