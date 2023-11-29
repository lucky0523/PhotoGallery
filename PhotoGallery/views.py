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
logging.basicConfig(level=Static.LOG_LEVEL, format='%(asctime)s - %(name)s %(levelname)s - %(message)s')
logger = logging.getLogger(LOG_TAG)


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
        print(dlist)
        dlist.sort(reverse=True)
        return render(request, 'navigation.html', context)


def resolving(request):
    for sub_path in os.scandir(Static.PATH_UNSORTED_PHOTOS):
        if os.path.isfile(sub_path):
            model = PhotoInfo(path=os.path.relpath(sub_path))
            model.resolving()

    for sub_path in os.scandir(Static.PATH_UNSORTED_FILMS):
        if os.path.isfile(sub_path):
            model = PhotoInfo(path=os.path.relpath(sub_path))
            model.resolving_film()
    plist = PhotoInfo.objects.filter(is_film=0).order_by("-shooting_time")
    i = 0
    for p in plist:
        p.set_order(i)
        i = i + 1
    return HttpResponse('aaaaa')


def query_image(request):
    order_str = request.GET.get('order', -1)
    year_str = request.GET.get('year', -1)
    p = PhotoInfo.objects.all().filter(order_id=order_str).first()
    if p is None:
        view_dict = {'code': 404, 'status': 'Not found!'}
        return HttpResponse(json.dumps(view_dict, sort_keys=True, indent=4, separators=(',', ': ')))
    if p.is_film:
        nex = PhotoInfo.objects.all().order_by("order_id").filter(is_film=1).filter(order_id__gt=order_str).first()
        prev = PhotoInfo.objects.all().order_by("order_id").filter(is_film=1).filter(order_id__lt=order_str).all().last()
    else:
        if utils.is_number(year_str):
            if int(year_str) == -1:
                nex = PhotoInfo.objects.all().order_by("order_id").filter(order_id__gt=order_str).first()
                prev = PhotoInfo.objects.all().order_by("order_id").filter(order_id__lt=order_str).all().last()
            elif int(year_str) > Static.EARLIER_YEAR:
                nex = PhotoInfo.objects.filter(shooting_time__year=year_str).order_by("order_id").filter(order_id__gt=order_str).first()
                prev = PhotoInfo.objects.filter(shooting_time__year=year_str).order_by("order_id").filter(order_id__lt=order_str).all().last()
            else:
                nex = PhotoInfo.objects.filter(shooting_time__year__lte=Static.EARLIER_YEAR).order_by("order_id").filter(order_id__gt=order_str).first()
                prev = PhotoInfo.objects.filter(shooting_time__year__lte=Static.EARLIER_YEAR).order_by("order_id").filter(order_id__lt=order_str).all().last()
        else:
            view_dict = {'code': 404, 'status': 'Year error'}
            return HttpResponse(json.dumps(view_dict, sort_keys=True, indent=4, separators=(',', ': ')))

    view_dict = utils.photo_to_dict(p)
    view_dict['code'] = 200
    view_dict['next'] = -1
    view_dict['prev'] = -1
    if p.device in Static.DEVICES_DICT:
        view_dict['device'] = Static.DEVICES_DICT[p.device]
    else:
        view_dict['device'] = p.device
    if nex is not None:
        view_dict['next'] = nex.order_id
    if prev is not None:
        view_dict['prev'] = prev.order_id
    logger.info('Query one image: ' + str(view_dict))
    return HttpResponse(json.dumps(view_dict, sort_keys=True, indent=4, separators=(',', ': ')))


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


def img_viewer(request):
    return render(request, 'image_viewer.html')


def editor(request):
    id_str = request.GET.get('id', -1)
    photo = PhotoInfo.objects.filter(id=id_str).first()
    view_dict = utils.photo_to_dict(photo)
    context = {'item': view_dict}
    return render(request, 'image_viewer.html', context)


def edit_photo(request):
    id_str = request.POST.get('id', -1)
    body = request.body
    file_model = request.POST.get('file_model', -1)
    p = PhotoInfo.objects.filter(id=id_str).first()
    view_dict = {'code': 404, 'status': 'Not found!'}
    if p is not None:
        if file_model != -1:
            logger.info("Edit No.%s: %s" % (id_str, body.decode()))
            view_dict = {'code': 200}
            p.set_file_model(file_model)
    return HttpResponse(json.dumps(view_dict, sort_keys=True, indent=4, separators=(',', ': ')))


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


def reset(request):
    plist = PhotoInfo.objects.all()
    for p in plist:
        p.delete()
    utils.clear_dir(Static.PATH_SORTED_SHOW_PHOTOS)
    utils.clear_dir(Static.PATH_SORTED_THUMBNAIL_PHOTOS)
    utils.unsort_files(Static.PATH_SORTED_RAW_PHOTOS, Static.PATH_UNSORTED_PHOTOS)
    utils.unsort_files(Static.PATH_SORTED_RAW_FILMS, Static.PATH_UNSORTED_FILMS)
    return HttpResponse('bbbb')


def uploader(request):
    msg = ''
    if request.method == 'POST':
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            fs = FileSystemStorage()
            save_path = Static.PATH_UPLOADED
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            filename = fs.save(os.path.join(save_path, uploaded_file.name), uploaded_file)

            # 获取保存后的文件URL
            file_url = fs.url(filename)
            logger.info("File saved, url:", file_url)
            msg = "上传成功!"
        else:
            msg = "未选择文件！"
    else:
        pass
    photo_list = []
    for sub_path in os.scandir(Static.PATH_UPLOADED):
        if os.path.isfile(sub_path):
            model = PhotoInfo(path=os.path.relpath(sub_path))
            model.resolving(False, False)
            photo_list.append(utils.photo_to_dict(model))
            print(model)
    context = {'msg': msg, 'photos': photo_list}
    return render(request, 'img_manager.html', context)


def wx_verify(request):
    return HttpResponse('15496962470248715457')
