import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv

load_dotenv()
root_url = os.getenv('ROOT_URL')

urls_to_crawl = [root_url]
crawled_urls = set()
base_domain = urlparse(urls_to_crawl[0]).netloc

def get_soup(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    return soup

def get_images(soup, base_url):
    images = set()
    for img_tag in soup.find_all('img'):
        image = urljoin(base_url, img_tag['src'])
        images.add(image)
    return images

def is_relative(url):
    return urlparse(url).netloc == ''

def is_external(url, base_domain):
    parsed_url = urlparse(url)
    return parsed_url.netloc and parsed_url.netloc != base_domain

while urls_to_crawl:
    url = urls_to_crawl.pop(0)
    if url in crawled_urls and not is_external(url, base_domain):
        continue

    soup = get_soup(url)

    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        if href:
            full_url = urljoin(url, href) if is_relative(href) else href
            if not is_external(full_url, base_domain) and full_url not in crawled_urls:
                urls_to_crawl.append(full_url)

    crawled_urls.add(url)

    get_images(soup, url)
