import time
import requests
import os


class DockerImageCrawler():

    def __init__(self, url='http:/127.0.0.1:8000', username=None, password=None, **config_options):
        self.url = url
        self.DockerHubSourceRepoQueryURL = 'https://hub.docker.com/api/build/v1/source/?image='
        if(username == None or password == None):
            self.authEnabled = False
            self.get_interval = 60
        else:
            self.authEnabled = True
            self.get_interval = 0.5
        if(self.authEnabled):
            self.username = username
            self.password = password
            self.__dict__.update(**config_options)
            self.session = requests.Session()
            if hasattr(self, 'api_token'):
                self.session.headers[
                    'Authorization'] = 'token %s' % self.api_token
            elif hasattr(self, 'username') and hasattr(self, 'password'):
                self.session.auth = (self.username, self.password)

    def call_github_api(self, url):
        if(self.authEnabled):
            return self.session.get(url)
        else:
            return requests.get(url)

    def get_source_repo_name(self, image_name):
        res = requests.get(
            self.DockerHubSourceRepoQueryURL + image_name).json()
        try:
            if(len(res['objects']) == 0):
                return None
            elif(res['objects'][0]['provider'] == 'Github'):
                return res['objects'][0]['owner'] + '/' + res['objects'][0]['repository']
        except:  # error happends (invalid image name, API internal error...)
            return None

    def get_first_commit(self, repo_full_name):
        url = 'https://api.github.com/repos/{}/commits'.format(repo_full_name)
        req = self.call_github_api(url)
        json_data = req.json()
        if req.headers.get('Link'):
            page_url = req.headers.get('Link').split(',')[1].split(';')[
                0].split('<')[1].split('>')[0]
            req_last_commit = requests.get(page_url)
            first_commit = req_last_commit.json()
            first_commit_hash = first_commit[-1]['sha']
        else:
            first_commit_hash = json_data[-1]['sha']
        return first_commit_hash

    def get_all_commits_count(self, repo_full_name):
        url = 'https://api.github.com/repos/{}/contributors'.format(
            repo_full_name)
        req = self.call_github_api(url)
        try:
            json_data = req.json()[-1]
            commit_count = json_data['contributions']
            return commit_count
        except:
            time.sleep(self.get_interval)
            url = 'https://api.github.com/repos/{}/commits'.format(
                repo_full_name)
            req = self.call_github_api(url)
            commit_count = len(req.json())
            if(commit_count == 0):
                return -1
            else:
                return commit_count

    def get_dockerfile(self, repo_full_name):
        url = 'https://raw.githubusercontent.com/{}/master/Dockerfile'.format(
            repo_full_name)
        req = self.call_github_api(url)
        req_text = req.text
        if(req_text == '404: Not Found\n'):
            return 404
        return req_text

    def get_dockerfile_from_dockerhub(self, image_name):
        url = 'https://hub.docker.com/v2/repositories/{}/dockerfile/'.format(
            image_name)
        req = requests.get(url)
        try:
            # There may be three results: 404 page, objects not found JSON, and
            # contents JSON
            json_data = req.json()
            return(json_data['contents'])
        except:
            return None

    def get_dockerfile_commits(self, repo_full_name):
        url = 'https://api.github.com/repos/{}/commits?path=Dockerfile'.format(
            repo_full_name)
        req = self.call_github_api(url)
        json_data = req.json()
        dockerfile_commit_count = len(json_data)
        dockerfile_commits = {}
        if(dockerfile_commit_count == 0):
            dockerfile_commits['dockerfile_commit_count'] = 0
            dockerfile_commits['dockerfile_commit_date'] = []
            dockerfile_commits['dockerfile_commit_sha'] = []
            dockerfile_commits['dockerfile_commit_message'] = []
            return dockerfile_commits
        else:
            dockerfile_commits[
                'dockerfile_commit_count'] = dockerfile_commit_count
            dockerfile_commit_date = []
            dockerfile_commit_sha = []
            dockerfile_commit_message = []
            for i in range(dockerfile_commit_count):
                dockerfile_commit_date.append(
                    json_data[i]['commit']['committer']['date'])
                dockerfile_commit_sha.append(json_data[i]['sha'])
                dockerfile_commit_message.append(
                    json_data[i]['commit']['message'])
            dockerfile_commits[
                'dockerfile_commit_date'] = dockerfile_commit_date
            dockerfile_commits['dockerfile_commit_sha'] = dockerfile_commit_sha
            dockerfile_commits[
                'dockerfile_commit_message'] = dockerfile_commit_message
            return dockerfile_commits

    # Get Docker image description, star_count and pull_count from DockerHub
    def get_docker_image_info(self, image_name):
        url = 'https://hub.docker.com/v2/repositories/{}/'.format(image_name)
        req = requests.get(url)
        try:
            json_data = req.json()
        except:
            return None
        results = {}
        try:
            results['image_description'] = json_data['description']
        except:
            pass
        try:
            results['image_star_count'] = json_data['star_count']
        except:
            pass
        try:
            results['image_pull_count'] = json_data['pull_count']
        except:
            pass
        return results

    def get_docker_image_tag(self, image_name):
        url = 'https://hub.docker.com/v2/repositories/{}/tags/'.format(
            image_name)
        j = {}
        tags_name = []
        image_size = []
        image_updated_at = []
        req = requests.get(url)
        try:
            json_data = req.json()
            tags_count = json_data['count']
        except:
            return {'tags_count': -1}
        j['tags_count'] = tags_count
        next_url = json_data['next']
        for i in range(len(json_data['results'])):
            tags_name.append(json_data['results'][i]['name'])
            image_size.append(json_data['results'][i]['full_size'])
            image_updated_at.append(json_data['results'][i]['last_updated'])
        while(next_url != None):
            time.sleep(0.5)
            req = requests.get(next_url)
            json_data = req.json()
            try:
                json_data['count']
            except:
                break
            next_url = json_data['next']
            for i in range(len(json_data['results'])):
                tags_name.append(json_data['results'][i]['name'])
                image_size.append(json_data['results'][i]['full_size'])
                image_updated_at.append(
                    json_data['results'][i]['last_updated'])
        j['tags_name'] = tags_name
        j['image_size'] = image_size
        j['image_updated_at'] = image_updated_at
        return j

    def get_source_repo_name_task(self):
        while True:
            task_json = requests.get(
                self.url + '/get_source_repo_name_task/').json()
            source_repo_name = self.get_source_repo_name(
                task_json['image_name'])
            results = {'pk': task_json['pk'], 'reponame_task': True}
            if source_repo_name != None:
                results['source_repo_name'] = source_repo_name
            r = requests.post(self.url + '/dockerimage/', json=results)
            time.sleep(0.5)

    def docker_image_info_crawler_task(self):
        while True:
            task_json = requests.get(
                self.url + '/docker_image_info_crawler_task/').json()
            try:
                if(task_json['code'] == 400):  # No more images left
                    time.sleep(60)  # Try again one min later
                    continue
            except:
                pass
            image_name = task_json['image_name']
            source_repo_name = task_json['source_repo_name']
            if(source_repo_name == 'None'):
                continue  # Do nothing if the image does not have a source repo
            results = {'pk': task_json['pk'], 'imageinfo_task': True}
            repo_res = self.call_github_api(
                'https://api.github.com/repos/' + source_repo_name).json()
            if(self.authEnabled):
                repo_res = self.session.get(
                    'https://api.github.com/repos/' + source_repo_name).json()
            else:
                repo_res = requests.get(
                    'https://api.github.com/repos/' + source_repo_name).json()
            try:  # To check whether the repo exists on GitHub
                try_repo_name = repo_res['full_name']
            except:  # if the repo does not exist, return pk only
                r = requests.post(self.url + '/dockerimage/', json=results)
                continue
            try:
                results['repo_size'] = repo_res['size']
            except:
                pass
            try:
                results['license'] = repo_res['license']['key']
            except:
                pass
            keys = ['language', 'forks_count', 'stargazers_count', 'watchers_count', 'default_branch', 'open_issues_count', 'topics', 'has_issues', 'has_projects',
                    'has_wiki', 'has_pages', 'has_downloads', 'archived', 'pushed_at', 'created_at', 'updated_at', 'subscribers_count', 'network_count']
            for key in keys:
                try:
                    results[key] = repo_res[key]
                except:
                    pass

            latest_dockerfile = self.get_dockerfile(source_repo_name)
            if(latest_dockerfile != 404):
                results['latest_dockerfile'] = latest_dockerfile
                results['repo_commits_count'] = self.get_all_commits_count(
                    source_repo_name)
                # time.sleep(self.get_interval)
                dockerfile_commits = self.get_dockerfile_commits(
                    source_repo_name)
                # time.sleep(self.get_interval)
                results['dockerfile_commit_sha'] = dockerfile_commits[
                    'dockerfile_commit_sha']
                results['dockerfile_commit_date'] = dockerfile_commits[
                    'dockerfile_commit_date']
                results['dockerfile_commit_message'] = dockerfile_commits[
                    'dockerfile_commit_message']

            docker_image_tag = self.get_docker_image_tag(image_name)
            if(docker_image_tag['tags_count'] != -1):
                results['tags_count'] = docker_image_tag['tags_count']
                results['tags_name'] = docker_image_tag['tags_name']
                results['image_size'] = docker_image_tag['image_size']
                results['image_updated_at'] = docker_image_tag[
                    'image_updated_at']
            r = requests.post(self.url + '/dockerimage/', json=results)
            time.sleep(self.get_interval)

    # Identifier: imageinfo_task
    def crawl_all_images_info_task(self):
        while True:
            task_json = requests.get(
                self.url + '/crawl_all_images_info_task/').json()
            try:
                if(task_json['code'] == 400):  # No more images left
                    time.sleep(60)  # Try again one min later
                    continue
            except:
                pass
            image_name = task_json['image_name']
            results = {'pk': task_json['pk'], 'imageinfo_task': True}
            source_repo_name = self.get_source_repo_name(image_name)
            if (source_repo_name != None):
                results['source_repo_name'] = source_repo_name
                repo_res = self.call_github_api(
                    'https://api.github.com/repos/' + source_repo_name).json()
                if(self.authEnabled):
                    repo_res = self.session.get(
                        'https://api.github.com/repos/' + source_repo_name).json()
                else:
                    repo_res = requests.get(
                        'https://api.github.com/repos/' + source_repo_name).json()
                try_repo_name = False
                try:  # To check whether the repo exists on GitHub
                    try_repo_name = repo_res['full_name']
                    try_repo_name = True
                except:  # if the repo does not exist
                    try_repo_name = False
                if(try_repo_name):  # if the repo exists
                    try:
                        results['repo_size'] = repo_res['size']
                    except:
                        pass
                    try:
                        results['license'] = repo_res['license']['key']
                    except:
                        pass
                    keys = ['language', 'forks_count', 'stargazers_count', 'watchers_count', 'default_branch', 'open_issues_count', 'topics', 'has_issues', 'has_projects',
                            'has_wiki', 'has_pages', 'has_downloads', 'archived', 'pushed_at', 'created_at', 'updated_at', 'subscribers_count', 'network_count']
                    for key in keys:
                        try:
                            results[key] = repo_res[key]
                        except:
                            pass
                    latest_dockerfile = self.get_dockerfile(source_repo_name)
                    if(latest_dockerfile != 404):  # crawl the latest dockerfile from github source repo
                        results['dockerfile_source'] = 'GitHub'
                        results['latest_dockerfile'] = latest_dockerfile
                        results['repo_commits_count'] = self.get_all_commits_count(
                            source_repo_name)
                        # time.sleep(self.get_interval)
                        dockerfile_commits = self.get_dockerfile_commits(
                            source_repo_name)
                        # time.sleep(self.get_interval)
                        results['dockerfile_commit_sha'] = dockerfile_commits[
                            'dockerfile_commit_sha']
                        results['dockerfile_commit_date'] = dockerfile_commits[
                            'dockerfile_commit_date']
                        results['dockerfile_commit_message'] = dockerfile_commits[
                            'dockerfile_commit_message']
                    else:
                        # If the crawler can not get the latest dockerfile from
                        # GitHub, try to get it from DockerHub
                        latest_dockerfile = self.get_dockerfile_from_dockerhub(
                            image_name)
                        if(latest_dockerfile != None):
                            results['latest_dockerfile'] = latest_dockerfile
                            results['dockerfile_source'] = 'DockerHub'
                else:  # If the GitHub repo does not exist, try to get the latest dockerfile from DockerHub
                    latest_dockerfile = self.get_dockerfile_from_dockerhub(
                        image_name)
                    if(latest_dockerfile != None):
                        results['latest_dockerfile'] = latest_dockerfile
                        results['dockerfile_source'] = 'DockerHub'
            # If the image does not have a GitHub source repo, try to get the
            # latest dockerfile from DockerHub (may come from Bitbucket)
            if(source_repo_name == None):
                latest_dockerfile = self.get_dockerfile_from_dockerhub(
                    image_name)
                if(latest_dockerfile != None):
                    results['latest_dockerfile'] = latest_dockerfile
                    results['dockerfile_source'] = 'DockerHub'

            # Get Docker image tags
            docker_image_tag = self.get_docker_image_tag(image_name)
            if(docker_image_tag['tags_count'] != -1):
                results['tags_count'] = docker_image_tag['tags_count']
                results['tags_name'] = docker_image_tag['tags_name']
                results['image_size'] = docker_image_tag['image_size']
                results['image_updated_at'] = docker_image_tag[
                    'image_updated_at']

            # Get Docker image description, star count and pull count
            docker_image_info = self.get_docker_image_info(image_name)
            if(docker_image_info != None):
                for key in docker_image_info.keys():
                    results[key] = docker_image_info[key]
            r = requests.post(self.url + '/dockerimage/', json=results)
            time.sleep(self.get_interval)

    # Identifier: imageinfo_task
    def crawl_repo_by_name_match_task(self):
        while True:
            task_json = requests.get(
                self.url + '/crawl_all_images_info_task/').json()
            try:
                if(task_json['code'] == 400):  # No more images left
                    time.sleep(60)  # Try again one min later
                    continue
            except:
                pass
            image_name = task_json['image_name']
            results = {'pk': task_json['pk'], 'imageinfo_task': True}
            source_repo_name = image_name  # NameMatch
            repo_res = self.call_github_api(
                'https://api.github.com/repos/' + source_repo_name).json()
            if(self.authEnabled):
                repo_res = self.session.get(
                    'https://api.github.com/repos/' + source_repo_name).json()
            else:
                repo_res = requests.get(
                    'https://api.github.com/repos/' + source_repo_name).json()
            try_repo_name = False
            try:  # To check whether the repo exists on GitHub
                try_repo_name = repo_res['full_name']
                try_repo_name = True
            except:  # if the repo does not exist
                try_repo_name = False
            if(try_repo_name):  # if the repo exists, try to get the latest dockerfile and relevant info from the GitHub repo
                latest_dockerfile = self.get_dockerfile(source_repo_name)
                if(latest_dockerfile != 404):  # crawl the latest dockerfile from github source repo
                    results['dockerfile_source'] = 'NameMatch'
                    results['source_repo_name'] = source_repo_name
                    results['latest_dockerfile'] = latest_dockerfile
                    results['repo_commits_count'] = self.get_all_commits_count(
                        source_repo_name)
                    time.sleep(self.get_interval)
                    dockerfile_commits = self.get_dockerfile_commits(
                        source_repo_name)
                    time.sleep(self.get_interval)
                    results['dockerfile_commit_sha'] = dockerfile_commits[
                        'dockerfile_commit_sha']
                    results['dockerfile_commit_date'] = dockerfile_commits[
                        'dockerfile_commit_date']
                    results['dockerfile_commit_message'] = dockerfile_commits[
                        'dockerfile_commit_message']
                    try:
                        results['repo_size'] = repo_res['size']
                    except:
                        pass
                    try:
                        results['license'] = repo_res['license']['key']
                    except:
                        pass
                    keys = ['language', 'forks_count', 'stargazers_count', 'watchers_count', 'default_branch', 'open_issues_count', 'topics', 'has_issues',
                            'has_projects', 'has_wiki', 'has_pages', 'has_downloads', 'archived', 'pushed_at', 'created_at', 'updated_at', 'subscribers_count', 'network_count']
                    for key in keys:
                        try:
                            results[key] = repo_res[key]
                        except:
                            pass
            else:  # If the repo does not exist, do nothing
                pass
            r = requests.post(self.url + '/dockerimage/', json=results)
            time.sleep(self.get_interval)

if __name__ == '__main__':
    url = os.getenv('POSTURL')
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    task = os.getenv('TASK')  # RepoName / ImageInfo / AllIMageInfo / NameMatch
    if(url == None):
        url = 'http://127.0.0.1:8000'
    crawler = DockerImageCrawler(url, username, password)
    if(task == 'RepoName'):
        crawler.get_source_repo_name_task()
    elif(task == 'ImageInfo'):
        crawler.docker_image_info_crawler_task()
    elif(task == 'AllImageInfo'):
        crawler.crawl_all_images_info_task()
    elif(task == 'NameMatch'):  # Use issue3.sql to initialize the db
        crawler.crawl_repo_by_name_match_task()
    else:
        print('No task specified.')
