#!/usr/bin/python3
import requests
import urllib.parse
import contextlib
from bs4 import BeautifulSoup
import os
import csv
import sys

# All image urls are based on this url - there is also a listing of what is in
# the archive at this page. 
base_url = 'http://www.homermultitext.org/hmt-image-archive/E4/E4-Pages/'

def top_mss_data_urls(archive_url):
    """ Construct root urls for the MSS archives. 
        Different formatting on this page than the others. """
    archive_page = requests.get(archive_url)
    page = BeautifulSoup(archive_page.text)
    return [urllib.parse.urljoin(archive_url, link.attrs['href']) for link in page.select('h2 a')] 

def archive_urls(mss_url):
    """ Construct urls found in an MSS archive page. 
        First link is always "Parent Directory" and so is indexed out. """
    mss_page = requests.get(mss_url)
    mss_page = BeautifulSoup(mss_page.text)
    return [os.path.join(mss_url, link.attrs['href']) for link in mss_page.select('td a')][1:]

def collect_urls(top_url, csv_writer):
    # The E3-Multispectral directory is massive, and I don't want it just now. 
    if 'multispectral' in top_url.lower():
        return []
    def tag_file(url):
        """ Return the url in a tuple with a tag indicating the file type.
            If another folder, recurse into it. 
            Apache (or at least the version HMT are using) returns the same 
            content type for both tiff's and their MD5 hashes. """
        img_exts = ['.md5','.tiff','.tif', '.jpg', '.jpeg']
        if url.endswith('.md5'):
            return ['MD5', url]
        if any(url.endswith(img_ext) for img_ext in img_exts):
            return ['IMG', url]
        # If it is neither md5 or image we need to check the headers. 
        with contextlib.closing(requests.get(url, stream=True)) as r:
            content_type = r.headers['content-type']
        if content_type.startswith('text/html'):
            # i.e. is another directory. 
            return collect_urls(url, csv_writer)
        else:
            return ['OTHER', url]

    for url in archive_urls(top_url):
        csv_writer.writerow(tag_file(url))
    return

file_out = sys.argv[1]
with open(file_out, 'w') as csv_out:
    for url in top_mss_data_urls(base_url):
        collect_urls(url, csv.writer(csv_out))
