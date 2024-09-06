import os
import requests
from dotenv import load_dotenv
import time

start_time = time.time()

load_dotenv()
root_url = os.getenv('ROOT_URL')

def request_images(paths):
  response_statuses = []
  for path in paths:
    combined_url = root_url + path
    res = requests.get(combined_url)
    response_statuses.append(f'{res.status_code}: {combined_url}')
    print(f'{res.status_code}: {combined_url}')
  return response_statuses

source_file = 'image_urls_bm.txt'

with open(source_file, 'r') as image_urls_file:
  paths = [url.strip() for url in image_urls_file.readlines()]

response_statuses = request_images(paths)

output_path = f'image_request_results_{time.strftime("%Y%m%d%H%M")}.txt'
with open(output_path, 'w') as image_request_results_file:
  image_request_results_file.write('\n'.join(response_statuses))

end_time = time.time()
print(f'実行時間: {end_time - start_time:.2f}秒')