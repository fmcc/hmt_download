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
base_url = 'http://www.homermultitext.org/hmt-image-archive/'

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

def find_filter_urls(top_url):
    """ I did have something more complicated here, but really I just want a big list of 
    all the urls for a MSS for another script to deal with.  """
    if 'spectral' in top_url:
        return []
    img_exts = ['.md5','.tiff','.tif', '.jpg', '.jpeg']
    urls = []
    for url in archive_urls(top_url):
        if any(url.endswith(img_ext) for img_ext in img_exts):
            urls.append(url) 
        else:
            with contextlib.closing(requests.get(url, stream=True)) as r:
                content_type = r.headers['content-type']
            if content_type.startswith('text/html'):
                urls.extend(find_filter_urls(url))
            else:
                pass
    return urls

with open('all_links.txt', 'a') as links_out:
    for MSS in top_mss_data_urls(base_url):
        for url in find_filter_urls(MSS):
            links_out.write('%s\n' %url)
        
