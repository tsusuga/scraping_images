import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
from dotenv import load_dotenv
import time

start_time = time.time()

load_dotenv()
root_url = os.getenv('ROOT_URL')

def generate_news_index_urls(start_year=2000, end_year=2024):
    urls = []
    index = start_year
    while index <= end_year:
        urls.append(f"{root_url}/news/index{index}.html")
        index += 1
    return urls

urls_to_crawl = [root_url] + generate_news_index_urls()

crawled_urls = set()
base_domain = urlparse(urls_to_crawl[0]).netloc
all_found_images = []

with open('image_names_jpg.txt', 'r') as image_names_file:
# 検索する画像名のリスト
  image_names_to_search = [name.strip() for name in image_names_file.readlines()]

def get_soup(url):
    try:
        res = requests.get(url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html5lib')
        return soup
    except requests.exceptions.RequestException as e:
        print(f'Error: {e}')
        return None

def search_images(soup, base_url, image_names):
    found_images = []
    for img_tag in soup.find_all('img'):
        img_url = urljoin(base_url, img_tag['src'])
        img_name = img_url.split('/')[-1]
        if img_name in image_names:
            found_images.append((img_name, img_url, base_url))
    return found_images

def is_relative(url):
    return urlparse(url).netloc == ''

def is_external(url, base_domain):
    parsed_url = urlparse(url)
    return parsed_url.netloc and parsed_url.netloc != base_domain

def format_url(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme + '://' + parsed_url.netloc + parsed_url.path

def is_fragment_with(url):
    return '#' in url

def is_pdf(url):
    return url.lower().endswith('.pdf')

def is_https(url):
    return urlparse(url).scheme == 'https'

while urls_to_crawl:
    url = urls_to_crawl.pop(0)
    if url in crawled_urls or is_external(url, base_domain) or is_fragment_with(url):
        continue

    soup = get_soup(url)

    if soup is None:
        continue

    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        if href:
            full_url = urljoin(url, href) if is_relative(href) else href
            if is_https(full_url) and not is_external(full_url, base_domain) and full_url not in crawled_urls and not is_pdf(full_url):
                urls_to_crawl.append(full_url)
    print(f"検索中: {url}")
    crawled_urls.add(url)

    images = search_images(soup, url, image_names_to_search)
    all_found_images.extend(images)

    time.sleep(1)

# 結果をExcelに出力
end_time = time.time()
output_path = f'found_images_{time.strftime("%Y%m%d%H%M")}.xlsx'
df = pd.DataFrame(all_found_images, columns=['Image Name', 'Image URL', 'Page URL'])
df.to_excel(output_path, index=False)

print(f"検索結果が{output_path}に保存されました。")
print(f"処理時間: {end_time - start_time:.2f}秒")