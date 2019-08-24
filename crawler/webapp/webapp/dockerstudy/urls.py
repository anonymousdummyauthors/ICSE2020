from django.conf.urls import url
from django.urls import include

from . import views

app_name = 'dockerstudy'

urlpatterns = [
    url(r"^get_image_name_task/$", views.get_image_name_task, name='get_image_name_task'),
    url(r"^image_name/$", views.post_image_name, name='post_image_name'),
    url(r"^get_source_repo_name_task/$", views.get_source_repo_name_task, name='get_source_repo_name_task'),
    url(r"^docker_image_info_crawler_task/$", views.docker_image_info_crawler_task, name='docker_image_info_crawler_task'),
    url(r"^crawl_all_images_info_task/$", views.crawl_all_images_info_task, name='crawl_all_images_info_task'),    
    url(r"^dockerimage/$", views.dockerimage, name='dockerimage')
]
