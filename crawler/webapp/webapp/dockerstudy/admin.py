from django.contrib import admin

from . import models


class DockerImageNameAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'original_id', 'image_name']

class PageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'page', 'last_sent', 'tag']

class DockerImageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'image_name', 'source_repo_name', 'last_sent', 'reponame_task', 'imageinfo_task', 'latest_dockerfile', 'dockerfile_source', 'tags_count', 'tags_name', 'image_size', 'image_updated_at', 'image_pull_count', 'image_star_count', 'repo_commits_count', 'dockerfile_commit_sha', 'dockerfile_commit_date',
                    'dockerfile_commit_message', 'language', 'forks_count', 'stargazers_count', 'watchers_count', 'repo_size', 'default_branch', 'open_issues_count', 'topics', 'has_issues', 'has_projects', 'has_wiki', 'has_pages', 'has_downloads', 'archived', 'pushed_at', 'created_at', 'updated_at', 'subscribers_count', 'network_count', 'license', 'image_description']


admin.site.register(models.DockerImageName, DockerImageNameAdmin)
admin.site.register(models.Page, PageAdmin)
admin.site.register(models.DockerImage, DockerImageAdmin)