
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
    print('Delete Page')
    models.DockerImageName.objects.all().delete()
    print('Delete DockerImageName')
except:
    print('nothing to delete')

df=pd.DataFrame()
df['page']=pd.RangeIndex(1,40001)
df['last_sent']=pd.Series()
df['tag']=pd.Series()
print('Loading initial data into the db...')

max_num_rows = df.shape[0]

print('num of rows to be added:', max_num_rows)

all_data = []


for i in range(max_num_rows):
    row = df.iloc[i, :]
    item = models.Page()
    item.page = row['page']
    all_data.append(item)

print('Bulk Saving...')

models.Page.objects.bulk_create(all_data, batch_size=999)