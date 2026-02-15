import json
import logging
import os
import random

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q

from PhotoGallery.common import Static, utils
from PhotoInfo.models import PhotoInfo

LOG_TAG = '[PhotoGallery.views] '
logging.basicConfig(level=Static.LOG_LEVEL, force=True, format='%(asctime)s - %(name)s %(levelname)s - %(message)s')
logger = logging.getLogger(LOG_TAG)

# interface
def nav(request):
    dlist = []
    if not os.path.exists(Static.PATH_SORTED_SHOW_PHOTOS):
        return render(request, 'navigation.html')
    else:
        for sub_path in os.scandir(Static.PATH_SORTED_SHOW_PHOTOS):
            if os.path.isdir(sub_path):
                if utils.is_number(os.path.basename(sub_path)):
                    if int(os.path.basename(sub_path)) <= Static.EARLIER_YEAR:
                        if str(Static.EARLIER_YEAR) not in dlist:
                            dlist.append(str(Static.EARLIER_YEAR))
                    else:
                        dlist.append(os.path.basename(sub_path))
                else:
                    dlist.append(os.path.basename(sub_path))
        context = {'PhotoDictionary': dlist}
        logger.info(f'PhotoDictionary: {dlist}')
        dlist.sort(reverse=True)
        return render(request, 'navigation.html', context)

# interface
def resolving(request):
    for sub_path in os.scandir(Static.PATH_UNSORTED_PHOTOS):
        if utils.is_photo_file(sub_path):
            model = PhotoInfo(path=os.path.relpath(sub_path))
            model.resolving_digital()

    for sub_path in os.scandir(Static.PATH_UNSORTED_FILMS):
        if utils.is_photo_file(sub_path):
            model = PhotoInfo(path=os.path.relpath(sub_path))
            model.resolving_film()
    plist = PhotoInfo.objects.filter(is_film=0).order_by("-shooting_time")
    i = 0
    for p in plist:
        p.set_order(i)
        i = i + 1
    return HttpResponse('resolve done')

# internal interface
def query_image(request):
    order_str = request.GET.get('order', -1)
    year_str = request.GET.get('year', -1)
    p = PhotoInfo.objects.all().filter(order_id=order_str).first()
    if p is None:
        view_dict = {'code': 404, 'status': 'Not found!'}
        return HttpResponse(json.dumps(view_dict, sort_keys=True, indent=4, separators=(',', ': ')))
    if p.is_film:
        nex = PhotoInfo.objects.all().order_by("order_id").filter(is_film=1).filter(order_id__gt=order_str).first()
        prev = PhotoInfo.objects.all().order_by("order_id").filter(is_film=1).filter(
            order_id__lt=order_str).all().last()
    else:
        if utils.is_number(year_str):
            if int(year_str) == -1:
                nex = PhotoInfo.objects.all().order_by("order_id").filter(order_id__gt=order_str).first()
                prev = PhotoInfo.objects.all().order_by("order_id").filter(order_id__lt=order_str).all().last()
            elif int(year_str) > Static.EARLIER_YEAR:
                nex = PhotoInfo.objects.filter(shooting_time__year=year_str).order_by("order_id").filter(
                    order_id__gt=order_str).first()
                prev = PhotoInfo.objects.filter(shooting_time__year=year_str).order_by("order_id").filter(
                    order_id__lt=order_str).all().last()
            else:
                nex = PhotoInfo.objects.filter(shooting_time__year__lte=Static.EARLIER_YEAR).order_by(
                    "order_id").filter(order_id__gt=order_str).first()
                prev = PhotoInfo.objects.filter(shooting_time__year__lte=Static.EARLIER_YEAR).order_by(
                    "order_id").filter(order_id__lt=order_str).all().last()
        else:
            view_dict = {'code': 404, 'status': 'Year error'}
            return HttpResponse(json.dumps(view_dict, sort_keys=True, indent=4, separators=(',', ': ')))

    view_dict = utils.photo_to_dict(p)
    view_dict['code'] = 200
    view_dict['next'] = -1
    view_dict['prev'] = -1
    view_dict['device'] = utils.get_device_name(p)
    if nex is not None:
        view_dict['next'] = nex.order_id
    if prev is not None:
        view_dict['prev'] = prev.order_id
    logger.info('Query one image: ' + str(view_dict))
    return HttpResponse(json.dumps(view_dict, sort_keys=True, indent=4, separators=(',', ': ')))

# internal interface
def query_list(request):
    homepage = request.GET.get('homepage', 0)
    year = request.GET.get('year', 1)
    view_list = []
    if int(homepage) > 0:
        plist = PhotoInfo.objects.all().order_by("order_id")
    else:
        if year == Static.KEY_FILMS:
            # 胶片
            plist = PhotoInfo.objects.filter(is_film=1).order_by("order_id")
        elif year == str(Static.EARLIER_YEAR):
            plist = PhotoInfo.objects.filter(shooting_time__year__lte=Static.EARLIER_YEAR).order_by("order_id")
        else:
            # 数码
            plist = PhotoInfo.objects.filter(shooting_time__year=year).order_by("order_id")
    for p in plist:
        # p.read_exif()
        view_dict = utils.photo_to_dict(p)

        view_list.append(view_dict)
    # if int(randomly) > 0:
    # random.shuffle(view_list)

    context = {'PageData': view_list}
    if request.method == 'POST':
        return render(request, 'gallery.html', context)
    else:
        return render(request, 'gallery.html', context)

# interface
def img_viewer(request):
    return render(request, 'image_viewer.html')

# interface
def editor(request):
    msg = ''
    id_str = request.GET.get('id', -1)
    qlist = PhotoInfo.objects.all().order_by("order_id")
    photo_list = []
    for photo in qlist:
        photo_list.append(utils.photo_to_dict(photo))
    context = {'msg': msg, 'photos': photo_list}
    return render(request, 'editor.html', context)

# interface
def get_all_films(request):
    plist = PhotoInfo.objects.filter(is_film=1)
    l = []
    for p in plist:
        f = {
            'id': p.id,
            'film_model': p.film_model
        }
        l.append(f)
    return HttpResponse(json.dumps(l, sort_keys=True, indent=4, separators=(',', ': ')))

# test interface
def reset(request):
    plist = PhotoInfo.objects.all()
    for p in plist:
        p.delete()
    utils.clear_dir(Static.PATH_SORTED_SHOW_PHOTOS)
    utils.clear_dir(Static.PATH_SORTED_THUMBNAIL_PHOTOS)
    utils.unsort_files(Static.PATH_SORTED_RAW_PHOTOS, Static.PATH_UNSORTED_PHOTOS)
    utils.unsort_files(Static.PATH_SORTED_RAW_FILMS, Static.PATH_UNSORTED_FILMS)
    return HttpResponse('reset done')

# interface
def uploader(request):
    # action有两种，upload和add_to_album
    # upload是上传至缓冲区，add_to_album是添加至相册
    msg = ''
    action = request.POST.get('action', -1)
    if request.method == 'POST':
        if action == 'upload_to_buffer':
            is_film = request.POST.get('is_film', -1) == "True"
            file_mtime = request.POST.get('file_mtime', None)
            if 'file' in request.FILES:
                uploaded_file = request.FILES['file']
                fs = FileSystemStorage()
                save_path = Static.PATH_UPLOADED
                if is_film:
                    logger.info("Upload film photo")
                    save_path = Static.PATH_UPLOADED_FILMS
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                filepath = fs.save(os.path.join(save_path, uploaded_file.name), uploaded_file)

                # 恢复文件的最后修改时间
                if file_mtime:
                    try:
                        mtime = int(file_mtime) / 1000.0
                        os.utime(filepath, (mtime, mtime))
                        logger.info(f"Restored file mtime: {filepath} -> {file_mtime}")
                    except Exception as e:
                        logger.error(f"Failed to set file mtime: {e}")

                # 获取保存后的文件URL
                file_url = fs.url(filepath)
                logger.info("File saved, url:", file_url)

                msg = "上传成功!"
            else:
                msg = "未选择文件！"
        elif action == 'add_to_album':
            amount = request.POST.get('amount', -1)
            is_film = request.POST.get('is_film', -1) == "True"
            if amount == 'one':
                path = request.POST.get('path', -1)
                logger.info('Add one photo: {}'.format(path))
                add_one(path, is_film)
                msg = '已添加一张'
            elif amount == 'all':
                logger.info('Add all photo')
                add_all(Static.PATH_UPLOADED)
                msg = '已添加全部'
        elif action == 'remove_from_buffer':
            path = request.POST.get('path', -1)
            logger.info('Remove one photo: {}'.format(path))
            if os.path.exists(path):
                os.remove(path)
            msg = '已移除: '+str(path)
    else:
        pass
    logger.info("扫描UPLOADED文件夹")
    photo_list = []
    for sub_path in os.scandir(Static.PATH_UPLOADED):
        if utils.is_photo_file(sub_path):
            model = PhotoInfo(path=os.path.relpath(sub_path))
            model.resolving_digital(False, False)
            base_name = os.path.splitext(sub_path.name)[0]
            thumbnail_name = f"{base_name}{Static.SUFFIX_THUMBNAIL}"
            thumbnail_path = os.path.relpath(os.path.join(Static.PATH_UPLOADED_TEMP, thumbnail_name))
            if not utils.is_photo_file(thumbnail_path):
                #生产缩略图，文件存放在PATH_UPLOADED_TEMP，缩略图与原图同名
                logger.info("Thumbnail not exist, make it: {}".format(sub_path.name))
                model.thumbnail_path = utils.make_show_image(sub_path, Static.SIZE_THUMBNAIL, Static.PATH_UPLOADED_TEMP, sub_path.name)
            else:
                logger.info("Thumbnail exist: {}".format(thumbnail_path))
                model.thumbnail_path = thumbnail_path
            logger.info('Show a cached photo: {}'.format(model.__dict__))
            photo_list.append(utils.photo_to_dict(model))
    for sub_path in os.scandir(Static.PATH_UPLOADED_FILMS):
        if utils.is_photo_file(sub_path):
            model = PhotoInfo(path=os.path.relpath(sub_path))
            model.resolving_film(False)
            photo_list.append(utils.photo_to_dict(model))

    utils.clean_uploaded_temp()

    context = {'msg': msg, 'photos': photo_list}
    return render(request, 'uploader.html', context)

# internal interface
def add_photo(request):
    msg = ''
    if request.method == 'POST':
        one = request.POST.get('one', -1) == "True"
        is_film = request.POST.get('is_film', -1) == "True"
        if one:
            path = request.POST.get('path', -1)[1:]
            logger.info('Add one photo: {}'.format(path))
            add_one(path, is_film)
            msg = '已添加一张'
            pass
        else:
            logger.info('Add all photo')
            add_all(Static.PATH_UPLOADED)
            add_all(Static.PATH_UPLOADED_FILMS, Static.KEY_FILM)
            msg = '已添加全部'
    html = ("<html><body>%s<br><br>"
            "<a href=\"/\">返回首页</a><br>"
            "<a href=\"/editor\">编辑图片</a><br>"
            "<a href=\"/uploader\">继续上传</a>"
            "</body></html>") % msg
    return HttpResponse(html)


def add_all(path, film_or_digital=Static.KEY_DIGITAL):
    for sub_path in os.scandir(path):
        if utils.is_photo_file(sub_path):
          model = PhotoInfo(path=os.path.relpath(sub_path))
          model.resolving(True, film_or_digital)

    plist = PhotoInfo.objects.filter(is_film=0).order_by("-shooting_time")
    i = 0
    for p in plist:
        p.set_order(i)
        i = i + 1


def add_one(path, is_film=False):
    if is_film:
        model = PhotoInfo(path=path)
        model.resolving_film()
    else:
        model = PhotoInfo(path=path)
        model.resolving_digital()
        plist = PhotoInfo.objects.filter(is_film=0).order_by("-shooting_time")
        i = 0
        for p in plist:
            p.set_order(i)
            i = i + 1
    
# interface
def action(request):
    logger.info('Action request: %s', request.GET)
    msg = ''
    id_str = request.GET.get('id', -1)
    action = request.GET.get('act', -1)
    logger.info('Modifying: action=%s, id=%s', action, id_str)
    idd = int(id_str)
    if action == 'del':
        p = PhotoInfo.objects.all().filter(id=idd).first()
        if p is not None:
            utils.delete_photo(p)
            msg = '已删除' + id_str
    elif action == 'modify':
        longitude = request.GET.get('longitude', -1)
        latitude = request.GET.get('latitude', -1)
        p = PhotoInfo.objects.all().filter(id=idd).first()
        if p is not None:
            if latitude != 'None' and longitude != 'None':
                if utils.is_number(latitude):
                    if utils.is_number(longitude):
                        p.set_position(longitude, latitude)
                        logger.info('Modify position, longitude=%s, latitude=%s' % (longitude, latitude))
                    else:
                        logger.error('longitude is not number!!')
                else:
                    logger.error('Latitude is not number!!')
            else:
                logger.error('Latitude or longitude is None!!')
    elif action == 'reset':
        p = PhotoInfo.objects.all().filter(id=idd).first()
        if p is not None:
            utils.reset_photo(p)
            msg = '已重置' + id_str
    html = ("<html><body>%s<br><br>"
            "<a href=\"/\">返回首页</a><br>"
            "<a href=\"/editor\">编辑图片</a><br>"
            "<a href=\"/uploader\">继续上传</a>"
            "</body></html>") % msg
    return HttpResponse(html)

# interface
def wx_verify(request):
    return HttpResponse('15496962470248715457')

# test interface
def position_picker(request):
    return render(request, 'map_position_picker.html', {'message': "Hello World!"})
