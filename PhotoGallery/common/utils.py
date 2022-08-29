import logging
import os
import shutil

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
