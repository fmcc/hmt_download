from celery import Celery
from contextlib import closing
import hashlib
import requests 
import os
import subprocess

app = Celery('tasks', backend='amqp', broker='amqp://')

@app.task
def download_img(dest, url):
    """ Downloads and saves the file to the given destination. """
    req = requests.get(url, stream=True)
    with open(dest, 'wb') as img_out:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                img_out.write(chunk)
                img_out.flush()
    return dest

def _calculate_img_hash(img_path):
    """ Iterates over image and calculates its md5 hash. """
    img_hash = hashlib.md5()
    with open(img_path, 'rb') as img:
        chunk = img.read(1024)
        while chunk:
            img_hash.update(chunk)
            chunk = img.read(1024)
    return img_hash.hexdigest()

@app.task
def verify_img(dest, url):
    """ Verifies the image against its md5 hash """
    hash_location = url + '.md5'
    remote_hash = requests.get(hash_location)
    orig_hash = remote_hash.text.split()[-1]
    new_hash = _calculate_img_hash(dest)
    if orig_hash != new_hash:
        return "Files not the same"
    return dest

@app.task 
def convert_img(dest):
    """ Convert tiff to jpeg and delete tiff to save on size. """
    if any(dest.endswith(img_ext) for img_ext in ['tif','tiff']):
        jpg_path = os.path.splitext(dest)[0] + '.jpg'
        subprocess.call(['convert', dest, jpg_path])
        os.remove(dest)
        return jpg_path
    else:
        return dest 

