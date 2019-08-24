import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.settings')
import django

django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Delete all if necessary
# User.objects.all().delete()

try:
    User.objects.create_superuser('admin', 'changyua@ualberta.ca', 'pass')
except Exception:
    print("Admin already exists!")

from dockerstudy import models
import pandas as pd

# Delete all if necessary
try:
    models.Page.objects.all().delete()
    models.DockerImage.objects.all().delete()
except:
    print('nothing to delete')


print('Loading the data from file...')

# data_file_name = '../data/mytable.csv'
# df=pd.DataFrame()
# df['page']=pd.RangeIndex(1,40001)
# df['last_sent']=pd.Series()
# df['tag']=pd.Series()
# print('Loading models onto the db...')
data_file_name = '../data/tags_init.csv'
df=pd.read_csv(data_file_name)
# max_num_rows = min(1000, df.shape[0])
max_num_rows = df.shape[0]

print('num of rows:', max_num_rows)

# all_pg = []
# for i in range(max_num_rows):
#     row = df.iloc[i, :]
#     pg = models.Page()
#     pg.page = row['page']
#     all_pg.append(pg)

all_di = []
# for i in range(max_num_rows):
#     row = df.iloc[i, :]
#     di = models.DockerImageInfo()
#     di.image_name = row['image_name']
#     all_di.append(di)

# for i in range(max_num_rows):
#     row = df.iloc[i, :]
#     di = models.DockerImageGitHubInfo()
#     di.image_name = row['image_name']
#     all_di.append(di)


# for i in range(max_num_rows):
#     row = df.iloc[i, :]
#     di = models.DockerfileInfo()
#     di.original_id = row['original_id']
#     di.repo_name = row['repo_name']
#     all_di.append(di)

# for i in range(max_num_rows):
#     row = df.iloc[i, :]
#     di = models.DockerImageTags()
#     di.original_id = row['original_id']
#     di.image_name = row['image_name']
#     all_di.append(di)

for i in range(max_num_rows):
    row = df.iloc[i, :]
    di = models.DockerImagePullCounts()
    di.original_id = row['original_id']
    di.image_name = row['image_name']
    all_di.append(di)


    # if row['Id'] == 210207849:
    #     ps = models.PythonSnippet()
    #     ps.original_id = row['Id']
    #     ps.post_id = row['PostId']
    #     ps.pred_post_block_version_id = row['PredPostBlockVersionId']
    #     ps.root_post_block_version_id = row['RootPostBlockVersionId']
    #     ps.length = row['Length']
    #     ps.line_count = row['LineCount']
    #     ps.tags = row['Tags']
    #     ps.content = row['Content']
    #     ps.save()


    
    # try:
    # ps.save()
    # except Exception:
    #     pass

print('Bulk Saving...')

models.DockerImagePullCounts.objects.bulk_create(all_di, batch_size=999)
