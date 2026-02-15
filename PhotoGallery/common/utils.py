import json
import logging
import os
import shutil
import requests
from PIL import Image, ExifTags
import pillow_heif
from urllib.parse import urlencode

# 注册 HEIC 格式支持
pillow_heif.register_heif_opener()

from PhotoGallery.common import Static

LOG_TAG = '[PhotoGallery.utils] '
logging.basicConfig(level=Static.LOG_LEVEL, format='%(asctime)s - %(name)s %(levelname)s - %(message)s')
logger = logging.getLogger(LOG_TAG)


def is_number(s):
    try:  # 如果能运⾏ float(s) 语句，返回 True（字符串 s 是浮点数）
        float(s)
        return True
    except ValueError:  # ValueError 为 Python 的⼀种标准异常，表⽰"传⼊⽆效的参数"
        pass  # 如果引发了 ValueError 这种异常，不做任何事情（pass：不做任何事情，⼀般⽤做占位语句）
    try:
        import unicodedata  # 处理 ASCII 码的包
        unicodedata.numeric(s)  # 把⼀个表⽰数字的字符串转换为浮点数返回的函数
        return True
    except (TypeError, ValueError):
        pass
        return False


def photo_to_dict(photo):
    if photo.show_path is None or photo.show_path == '':
        # 上传页面生成预览图片的信息时走这里
        view_dict = {'image': "/" + photo.path,
                     'file_model': photo.film_model,
                     'is_film': photo.is_film,
                     'formatted_name': photo.formatted_name,
                     'time': photo.shooting_time,
                     'thumbnail': photo.thumbnail_path}
        if photo.device in Static.DEVICES_DICT:
            view_dict['device'] = Static.DEVICES_DICT[photo.device]
        else:
            view_dict['device'] = photo.device
    elif photo.is_film:
        view_dict = {'id': photo.id,
                     'order': photo.order_id,
                     'image': photo.show_path[1:],
                     'thumbnail': photo.thumbnail_path[1:],
                     'is_film': photo.is_film,
                     'file_model': photo.film_model}
    else:
        view_dict = {'id': photo.id,
                     'order': photo.order_id,
                     'image': photo.show_path[1:],
                     'thumbnail': photo.thumbnail_path[1:],
                     'formatted_name': photo.formatted_name,
                     'is_film': photo.is_film,
                     'iso': photo.iso,
                     'f_number': photo.f_number,
                     'expo': photo.expo_time,
                     'focal_length': photo.equivalent_focal_length,
                     'city': photo.city,
                     'district': photo.district,
                     'longitude': photo.longitude,
                     'latitude': photo.latitude,
                     'time': photo.shooting_time.strftime("%Y-%m-%d %H:%M:%S")}
        if photo.device in Static.DEVICES_DICT:
            view_dict['device'] = Static.DEVICES_DICT[photo.device]
        else:
            view_dict['device'] = photo.device
    return view_dict


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
        if orientation in exif:
            if exif[orientation] == 3:
                img = img.rotate(180, expand=True)
            elif exif[orientation] == 6:
                img = img.rotate(270, expand=True)
            elif exif[orientation] == 8:
                img = img.rotate(90, expand=True)
    return img


def make_square_thumbnail(src_file, side, dstpath, dstname):
    logger.info("Make square thumbnail,dstpath %s, dstname %s" % (dstpath, dstname))
    if not dstpath.endswith('/'):
        dstpath = dstpath + '/'
    if not os.path.exists(dstpath):
        os.makedirs(dstpath)
    #缩略图后缀统一改成jpg
    base_name, ext = os.path.splitext(dstname)
    dstname = base_name + '.jpg'

    img = open_and_rotate(src_file)
    width, height = img.size
    if width < height:
        crop_img = img.crop((0, int((height - width) / 2), width, int((height - width) / 2) + width))
    else:
        crop_img = img.crop((int((width - height) / 2), 0, int((width - height) / 2) + height, height))
    img.close()
    crop_img = crop_img.resize((side, side), Image.LANCZOS)
    if crop_img.mode != 'RGB':
        crop_img = crop_img.convert('RGB')
    crop_img.save(dstpath + dstname, quality=80)
    logger.info("Save thumbnail -> %s" % (dstpath + dstname))
    return dstpath + dstname


def make_show_image(src_file, max_side, dstpath, dstname):
    logger.info("Make show image,dstpath:%s, dstname:%s, max_side:%s" % (dstpath, dstname, max_side))
    if not dstpath.endswith('/'):
        dstpath = dstpath + '/'
    if not os.path.exists(dstpath):
        os.makedirs(dstpath)
    #缩略图后缀统一改成jpg
    base_name, ext = os.path.splitext(dstname)
    dstname = base_name + '.jpg'

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
    crop_img = img.resize((resize_width, resize_height), Image.LANCZOS)
    if crop_img.mode != 'RGB':
        crop_img = crop_img.convert('RGB')
    crop_img.save(dstpath + dstname, quality=80)
    img.close()
    logger.info("Save resize image -> %s" % (dstpath + dstname))
    return dstpath + dstname


def sexagesimal2decimal(xtitude_str):
    deg, min, sec = [x.replace(' ', '') for x in str(xtitude_str).split(',')]
    return float(deg) + ((float(min) + (float(sec.split('/')[0]) / float(sec.split('/')[-1]) / 60)) / 60)

""" 百度逆地理编码接口，不支持中国以外的经纬度
def decode_address_from_gps(lat, lng):
    '''
    使用Geocoding API把经纬度坐标转换为结构化地址。
    :param GPS:
    :return:
    '''
    logger.info("Decode address from gps, lat: %s, lng: %s" % (lat, lng))
    baidu_map_api = "https://api.map.baidu.com/reverse_geocoding/v3/?ak={0}&extensions_poi=1&entire_poi=1&sort_strategy=distance&output=json&coordtype=bd09ll&location={1}%2C{2}".format(
        Static.KEY_BAIDUMAP_SERVER_SECRET_AK, lng, lat)
    logger.info('Baidu Map API: ' + baidu_map_api)
    response = requests.get(baidu_map_api)
    content = response.text.replace("renderReverse&&renderReverse(", "")[:-1]
    baidu_map_address = json.loads(response.text)
    status = baidu_map_address["status"]
    formatted_address = ""
    business = ""
    province = ""
    city = ""
    district = ""
    if status == 0:
        logger.info(baidu_map_address)
        formatted_address = baidu_map_address["result"]["formatted_address"]
        business = baidu_map_address["result"]["business"]
        province = baidu_map_address["result"]["addressComponent"]["province"]
        city = baidu_map_address["result"]["addressComponent"]["city"]
        district = baidu_map_address["result"]["addressComponent"]["district"]
        location = baidu_map_address["result"]["sematic_description"]
        logger.info("Decode geo [%.2f, %.2f] -> %s,%s,%s" % (lng, lat, province, city, district))
    else:
        logger.error(baidu_map_address)

    return province, city, district
"""

"""
使用BigDataCloud的接口根据经纬度获取地址信息
:param lat: 纬度
:param lng: 经度
:return: province, city, district, country
"""
def decode_address_from_gps(lat, lng):
    logger.info(f"Decode address from GPS using BigDataCloud, lat: {lat}, lng: {lng}")

    try:
        # BigDataCloud反向地理编码API
        api_url = f"https://api.bigdatacloud.net/data/reverse-geocode-client"
        params = {
            'latitude': lat,
            'longitude': lng,
            'localityLanguage': 'zh',  # 使用中文返回结果
            'key': Static.KEY_BIGDATACLOUD_API_KEY
        }
        
        # 构建完整的URL用于调试
        full_url = f"{api_url}?{urlencode(params)}"
        logger.info(f"Request URL: {full_url}")
        
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()  # 检查HTTP错误
        
        data = response.json()
        logger.info(f"BigDataCloud API response: {data}")
        
        # 提取地址信息
        country = data.get('countryName', '')
        province = data.get('principalSubdivision', '')
        city = data.get('city', '')
        district = data.get('locality', '')
        
        # 处理可能的空值
        if not city:
            city = data.get('principalSubdivision', '')
        if not district:
            district = data.get('city', '')
        
        logger.info(f"Decoded address: country={country}, province={province}, city={city}, district={district}")
        return country, province, city, district
        
    except Exception as e:
        logger.error(f"Error decoding address from GPS: {e}")
        return '', '', '', ''


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


def delete_photo(photo):
    try:
        os.remove(photo.thumbnail_path)
        os.remove(photo.show_path)
        os.remove(photo.path)
    except FileNotFoundError as e:
        logger.error(e)
    photo.delete()


def reset_photo(photo):
    os.remove(photo.thumbnail_path)
    os.remove(photo.show_path)
    if photo.is_film:
        move_file(photo.path, Static.PATH_UPLOADED_FILMS)
    else:
        move_file(photo.path, Static.PATH_UPLOADED)
    photo.delete()

def is_photo_file(file_name):
    if hasattr(file_name, 'name'):
        name = file_name.name
    else:
        name = os.path.basename(file_name)
    return os.path.isfile(file_name) and name.lower().endswith(Static.PIC_EXTS)

def clean_uploaded_temp():
    """
    清理 PATH_UPLOADED_TEMP 文件夹中多余的缩略图文件。
    如果在 PATH_UPLOADED 和 PATH_UPLOADED_FILMS 中找不到同名的源文件，则删除该缩略图。
    """
    if not os.path.exists(Static.PATH_UPLOADED_TEMP):
        logger.info("上传临时缩略图目录不存在，跳过清理")
        return

    for thumb in os.scandir(Static.PATH_UPLOADED_TEMP):
        if thumb.is_file() and thumb.name.lower().endswith('.jpg'):
            base_name = os.path.splitext(thumb.name)[0]
            # 构造可能的源文件名（支持常见原图扩展名）
            source_found = False
            for ext in Static.PIC_EXTS:
                source_file = base_name + ext
                if (os.path.isfile(os.path.join(Static.PATH_UPLOADED, source_file)) or
                        os.path.isfile(os.path.join(Static.PATH_UPLOADED_FILMS, source_file))):
                    source_found = True
                    break
            if not source_found:
                try:
                    os.remove(thumb.path)
                    logger.info("删除多余缩略图: %s", thumb.name)
                except Exception as e:
                    logger.error("删除缩略图失败 %s: %s", thumb.name, e)