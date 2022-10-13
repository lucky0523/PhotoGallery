import json
import logging
import os
import shutil
import requests
from PIL import Image, ExifTags

from PhotoGallery.common import Static

LOG_TAG = '[PhotoGallery.utils]'
logging.basicConfig(level=Static.LOG_LEVEL, format='%(asctime)s - %(name)s %(levelname)s - %(message)s')
logger = logging.getLogger(LOG_TAG)


def move_file(srcfile, dstpath, dstname=''):  # 移动文件函数，dstpath不可以加文件名
    if not dstpath.endswith('/'):
        dstpath = dstpath + '/'
    if not os.path.isfile(srcfile):
        logger.error("%s not exist!" % os.path.abspath(srcfile))
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


def open_and_rotate(src_file):
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
    return img


def make_square_thumbnail(src_file, side, dstpath, dstname):
    if not dstpath.endswith('/'):
        dstpath = dstpath + '/'
    if not os.path.exists(dstpath):
        os.makedirs(dstpath)
    img = open_and_rotate(src_file)
    width, height = img.size
    if width < height:
        crop_img = img.crop((0, int((height - width) / 2), width, int((height - width) / 2) + width))
    else:
        crop_img = img.crop((int((width - height) / 2), 0, int((width - height) / 2) + height, height))
    img.close()
    crop_img = crop_img.resize((side, side), Image.ANTIALIAS)
    crop_img.save(dstpath + dstname, quality=80)
    logger.info("Save thumbnail -> %s" % (dstpath + dstname))
    return dstpath + dstname


def make_show_image(src_file, max_side, dstpath, dstname):
    if not dstpath.endswith('/'):
        dstpath = dstpath + '/'
    if not os.path.exists(dstpath):
        os.makedirs(dstpath)
    img = open_and_rotate(src_file)
    width, height = img.size
    if max(max_side, width, height) == max_side:
        resize_width = width
        resize_height = height
    elif width < height:
        resize_height = max_side
        resize_width = int(width / (height / max_side))
    else:
        resize_width = max_side
        resize_height = int(height / (width / max_side))
    crop_img = img.resize((resize_width, resize_height), Image.ANTIALIAS)
    crop_img.save(dstpath + dstname, quality=80)
    img.close()
    logger.info("Save resize image -> %s" % (dstpath + dstname))
    return dstpath + dstname


def sexagesimal2decimal(xtitude_str):
    deg, min, sec = [x.replace(' ', '') for x in str(xtitude_str).split(',')]
    return float(deg) + ((float(min) + (float(sec.split('/')[0]) / float(sec.split('/')[-1]) / 60)) / 60)


def decode_address_from_gps(lat, lng):
    """
    使用Geocoding API把经纬度坐标转换为结构化地址。
    :param GPS:
    :return:
    """
    secret_key = 'zbLsuDDL4CS2U0M4KezOZZbGUY9iWtVf'
    baidu_map_api = "http://api.map.baidu.com/geocoder/v2/?ak={0}&callback=renderReverse&location={1},{2}s&output=json&pois=0".format(
        secret_key, lat, lng)
    response = requests.get(baidu_map_api)
    content = response.text.replace("renderReverse&&renderReverse(", "")[:-1]
    baidu_map_address = json.loads(content)
    formatted_address = baidu_map_address["result"]["formatted_address"]
    business = baidu_map_address["result"]["business"]
    province = baidu_map_address["result"]["addressComponent"]["province"]
    city = baidu_map_address["result"]["addressComponent"]["city"]
    district = baidu_map_address["result"]["addressComponent"]["district"]
    location = baidu_map_address["result"]["sematic_description"]
    logger.info("Decode geo [%.2f, %.2f] -> %s,%s,%s" % (lng, lat, province, city, district))
    return province, city, district


def clear_dir(dir_path):
    # os.walk会得到dir_path下各个后代文件夹和其中的文件的三元组列表，顺序自内而外排列，
    # 如 log下有111文件夹，111下有222文件夹：[('D:\\log\\111\\222', [], ['22.py']), ('D:\\log\\111', ['222'], ['11.py']), ('D:\\log', ['111'], ['00.py'])]
    for root, dirs, files in os.walk(dir_path, topdown=False):
        print(root)  # 各级文件夹绝对路径
        print(dirs)  # root下一级文件夹名称列表，如 ['文件夹1','文件夹2']
        print(files)  # root下文件名列表，如 ['文件1','文件2']
        # 第一步：删除文件
        for f in files:
            os.remove(os.path.join(root, f))  # 删除文件
        # 第二步：删除空文件夹
        for d in dirs:
            os.rmdir(os.path.join(root, d))  # 删除一个空目录


def unsort_files(scr_dir, dst_dir):
    for root, dirs, files in os.walk(scr_dir, topdown=False):
        for f in files:
            move_file(os.path.join(root, f), dst_dir)
