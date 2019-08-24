from django.db import models
from django.utils import timezone
from postgres_copy import CopyManager


# Create your models here.
class DockerImageName(models.Model):
    original_id = models.IntegerField(blank=False, null=False, unique=False)
    image_name = models.CharField(max_length=2048, blank=False, null=False)

    objects = CopyManager()

    def __unicode__(self):
        return '{} - {}'.format(self.id, self.original_id)

    def __str__(self):
        return self.__unicode__()

    def to_dict(self):
        return {
            'pk': self.id,
            'original_id': self.original_id,
            'image_name': self.image_name
        }


class Page(models.Model):
    page = models.IntegerField(blank=False, null=False, unique=True)
    last_sent = models.DateTimeField(default=None, blank=True, null=True)
    tag = models.TextField(blank=True, null=True)
    objects = CopyManager()

    def __unicode__(self):
        return '{} - {}'.format(self.id, self.page)

    def update_last_sent(self):
        self.refresh_from_db()
        self.last_sent = timezone.now()
        self.save()

    def __str__(self):
        return self.__unicode__()

    def to_dict(self):
        return {
            'page': self.page,
            'last_sent': self.last_sent,
            'tag': self.tag
        }

class DockerImage(models.Model):
    image_name = models.CharField(max_length=2048, blank=False, null=False)
    source_repo_name = models.CharField(max_length=2048, blank=True, null=True)
    last_sent = models.DateTimeField(default=None, blank=True, null=True)
    reponame_task=models.BooleanField(default=False)
    imageinfo_task=models.BooleanField(default=False)
    latest_dockerfile = models.TextField(blank=True, null=True)
    dockerfile_source = models.TextField(blank=True, null=True)
    tags_count = models.IntegerField(blank=True, null=True)
    tags_name = models.TextField(blank=True, null=True)
    image_size = models.TextField(blank=True, null=True)
    image_updated_at = models.TextField(default=None, blank=True, null=True)
    image_pull_count = models.IntegerField(blank=True, null=True)
    image_star_count = models.IntegerField(blank=True, null=True)
    repo_commits_count = models.IntegerField(blank=True, null=True)
    dockerfile_commit_sha = models.TextField(blank=True, null=True)
    dockerfile_commit_date = models.TextField(blank=True, null=True)
    dockerfile_commit_message = models.TextField(blank=True, null=True)
    language = models.TextField(blank=True, null=True)
    forks_count = models.IntegerField(blank=True, null=True)
    stargazers_count = models.IntegerField(blank=True, null=True)
    watchers_count = models.IntegerField(blank=True, null=True)
    repo_size = models.IntegerField(blank=True, null=True)
    default_branch = models.TextField(blank=True, null=True)
    open_issues_count = models.IntegerField(blank=True, null=True)
    topics = models.TextField(blank=True, null=True)
    has_issues = models.TextField(blank=True, null=True)
    has_projects = models.TextField(blank=True, null=True)
    has_wiki = models.TextField(blank=True, null=True)
    has_pages = models.TextField(blank=True, null=True)
    has_downloads = models.TextField(blank=True, null=True)
    archived = models.TextField(blank=True, null=True)
    pushed_at = models.DateTimeField(default=None, blank=True, null=True)
    created_at = models.DateTimeField(default=None, blank=True, null=True)
    updated_at = models.DateTimeField(default=None, blank=True, null=True)
    subscribers_count = models.IntegerField(blank=True, null=True)
    network_count = models.IntegerField(blank=True, null=True)
    license = models.TextField(blank=True, null=True)
    image_description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return '{}'.format(self.id)

    def update_last_sent(self):
        self.refresh_from_db()
        self.last_sent = timezone.now()
        self.save()

    def __str__(self):
        return self.__unicode__()

    def to_task_dict(self):
        return {
            'pk': self.id,
            'image_name':self.image_name,
            'source_repo_name':self.source_repo_name
            }

    def to_dict(self):
        return {
            'pk': self.id,
            'image_name':self.image_name,
            'source_repo_name':self.source_repo_name,
            'last_sent':self.last_sent,
            'reponame_task':self.reponame_task,
            'imageinfo_task':self.imageinfo_task,
            'latest_dockerfile':self.latest_dockerfile,
            'dockerfile_source':self.dockerfile_source,
            'tags_count':self.tags_count,
            'tags_name':self.tags_name,
            'image_size':self.image_size,
            'image_updated_at':self.image_updated_at,
            'image_pull_count':self.image_pull_count,
            'image_star_count':self.image_star_count,
            'repo_commits_count':self.repo_commits_count,
            'dockerfile_commit_sha':self.dockerfile_commit_sha,
            'dockerfile_commit_date':self.dockerfile_commit_date,
            'dockerfile_commit_message':self.dockerfile_commit_message,
            'language':self.language,
            'forks_count':self.forks_count,
            'stargazers_count':self.stargazers_count,
            'watchers_count':self.watchers_count,
            'repo_size':self.repo_size,
            'default_branch':self.default_branch,
            'open_issues_count':self.open_issues_count,
            'topics':self.topics,
            'has_issues':self.has_issues,
            'has_projects':self.has_projects,
            'has_wiki':self.has_wiki,
            'has_pages':self.has_pages,
            'has_downloads':self.has_downloads,
            'archived':self.archived,
            'pushed_at':self.pushed_at,
            'created_at':self.created_at,
            'updated_at':self.updated_at,
            'subscribers_count':self.subscribers_count,
            'network_count':self.network_count,
            'license':self.license,
            'image_description':self.image_description
            }