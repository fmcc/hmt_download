import sys
import os
from celery import chain
from tasks import *

source, root_dest = sys.argv[1], sys.argv[2]

with open(source) as urls_in:
    urls = [line.strip() for line in urls_in.readlines()]

new_path_tuples = [url.split('/')[-2:] for url in urls]

# Create the destination folders
if not os.path.exists(root_dest):
    os.mkdir(root_dest)
dir_names = set(items[0] for items in new_path_tuples)
for img_dir in dir_names:
    new_dir_path = os.path.join(root_dest, img_dir)
    if not os.path.exists(new_dir_path):
        os.mkdir(new_dir_path)
dest_paths = [os.path.join(root_dest, *path_parts) for path_parts in new_path_tuples]

for dest, url in zip(dest_paths, urls): 
    result = chain(download_img.s(dest, url), verify_img.s(url), convert_img.s())()
