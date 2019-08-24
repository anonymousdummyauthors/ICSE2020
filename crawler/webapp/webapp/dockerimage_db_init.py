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
    print('Delete DockerImage')
    models.DockerImage.objects.all().delete()
except:
    print('nothing to delete')

data_file_name = '../data/docker_image_name.csv'
print("Loading data from {} ....".format(data_file_name))
df = pd.read_csv(data_file_name, error_bad_lines=False, warn_bad_lines=False)
max_num_rows = df.shape[0]

print('num of rows to be added:', max_num_rows)

all_data = []

for i in range(max_num_rows):
    row = df.iloc[i, :]
    image = models.DockerImage()
    image.image_name = row['image_name']
    all_data.append(image)
    print(i,end='\r')

print('Bulk Saving...')

models.DockerImage.objects.bulk_create(all_data, batch_size=999)
