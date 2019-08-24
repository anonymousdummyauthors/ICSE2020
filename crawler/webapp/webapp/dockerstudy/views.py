from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from .models import DockerImageName
from .models import Page
from .models import DockerImage
import random
import json


@csrf_exempt
def post_image_name(request):
    body_unicode = request.body.decode('utf-8')
    jsondata = json.loads(body_unicode)
    image_dic = jsondata['image_list']
    if(image_dic=={}):
        return JsonResponse({
        'msg': 'Bad Request',
        'code': 502,
        })
    for key in image_dic.keys():
        image = DockerImageName(original_id=key, image_name=image_dic[key])
        image.save()
    page = get_object_or_404(Page, page=jsondata['page'])
    page.tag = 'Done'
    page.save(update_fields=['tag'])
    return JsonResponse({
        'msg': 'OK!',
        'code': 200,
    })


@csrf_exempt
def get_image_name_task(request):
    last_process_threshold = timezone.now() - timezone.timedelta(minutes=2)
    pages = Page.objects.filter(Q(last_sent__lte=last_process_threshold, tag__isnull=True) | Q(
        last_sent__isnull=True)).order_by('page')
    try:
        page = pages[0]
    except Exception:
        return HttpResponseBadRequest('No more pages left')
    page.update_last_sent()
    page.save(update_fields=["last_sent"])
    obj = page.to_dict()
    return JsonResponse(obj)

#Get source repo name only
#identifier: reponame_task
@csrf_exempt
def get_source_repo_name_task(request):
    last_process_threshold = timezone.now() - timezone.timedelta(minutes=2)
    images = DockerImage.objects.filter(Q(last_sent__lte=last_process_threshold, reponame_task=False) | Q(last_sent__isnull=True))
    try:
        image = images[0]
    except Exception:
        return HttpResponseBadRequest('No more images left')
    image.update_last_sent()
    image.save(update_fields=["last_sent"])
    obj = image.to_task_dict()
    return JsonResponse(obj)

#Crawl image info which has a source repo
#identifier: imageinfo_task
@csrf_exempt
def docker_image_info_crawler_task(request):
    last_process_threshold = timezone.now() - timezone.timedelta(minutes=2)
    images = DockerImage.objects.filter(Q(source_repo_name__isnull=False, last_sent__lte=last_process_threshold, imageinfo_task=False) | Q(source_repo_name__isnull=False, last_sent__isnull=True))
    try:
        image = images[0]
    except Exception:
        return JsonResponse({
        'msg': 'No more images left',
        'code': 400})
    image.update_last_sent()
    image.save(update_fields=["last_sent"])
    obj = image.to_task_dict()
    return JsonResponse(obj)

#Crawl image info, no matter it has a source repo or not
#identifier: imageinfo_task
# The last process threshold should be high, as some images may have thousands of tags.
@csrf_exempt
def crawl_all_images_info_task(request):
    last_process_threshold = timezone.now() - timezone.timedelta(minutes=30)
    images = DockerImage.objects.filter(Q(last_sent__lte=last_process_threshold, imageinfo_task=False) | Q(last_sent__isnull=True))
    try:
        image = images[0]
    except Exception:
        return JsonResponse({
        'msg': 'No more images left',
        'code': 400})
    image.update_last_sent()
    image.save(update_fields=["last_sent"])
    obj = image.to_task_dict()
    return JsonResponse(obj)

@csrf_exempt
def dockerimage(request):
    body_unicode = request.body.decode('utf-8')
    jsondata = json.loads(body_unicode)
    image = get_object_or_404(DockerImage, pk=int(jsondata['pk']))
    update_fields=list(jsondata.keys())
    update_fields.remove('pk')
    for key in update_fields:
        setattr(image,key,jsondata[key])
    image.save(update_fields=update_fields)
    return JsonResponse({
        'msg': 'OK!',
        'code': 200
    })
