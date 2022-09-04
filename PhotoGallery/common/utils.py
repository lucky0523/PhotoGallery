import logging
import os
import shutil

from PIL import Image, ExifTags

from PhotoGallery.common import Static

LOG_TAG = '[PhotoGallery.utils]'
logging.basicConfig(level=Static.LOG_LEVEL, format='%(asctime)s - %(name)s %(levelname)s - %(message)s')
logger = logging.getLogger(LOG_TAG)


def move_file(srcfile, dstpath, dstname=''):  # 移动文件函数，dstpath不可以加文件名
    if not dstpath.endswith('/'):
        dstpath = dstpath + '/'
    if not os.path.isfile(srcfile):
        logger.error("%s not exist!" % srcfile)
        return None
    else:
        if not os.path.exists(dstpath):
            os.makedirs(dstpath)
        spath, sname = os.path.split(srcfile)  # 分离文件名和路径
        if dstname is not None and dstname != '':  # 填了文件名的情况
            sname = dstname
        shutil.move(srcfile, dstpath + sname)  # 移动文件
        logger.info("Move %s -> %s" % (srcfile, dstpath + sname))
        return dstpath + sname


def make_square_thumbnail(src_file, side, dstpath, dstname):
    img = Image.open(src_file)
    try:
        exif = img._getexif()
    except AttributeError:
        exif = None

    if exif is not None:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        if exif[orientation] == 3:
            img = img.rotate(180, expand=True)
        elif exif[orientation] == 6:
            img = img.rotate(270, expand=True)
        elif exif[orientation] == 8:
            img = img.rotate(90, expand=True)

    width, height = img.size
    if not dstpath.endswith('/'):
        dstpath = dstpath + '/'
    if not os.path.exists(dstpath):
        os.makedirs(dstpath)
    if width < height:
        crop_img = img.crop((0, int((height - width) / 2), width, int((height - width) / 2) + width))
    else:
        crop_img = img.crop((int((width - height) / 2), 0, int((width - height) / 2) + height, height))
    crop_img = crop_img.resize((side, side), Image.ANTIALIAS)
    crop_img.save(dstpath + dstname)
    logger.info("Save thumbnail -> %s" % (dstpath + dstname))
    return dstpath + dstname
