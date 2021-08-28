import argparse
import concurrent.futures

import requests
import logging
from bs4 import BeautifulSoup

from proxy import Proxy
from utils import ProxyTypeMapper, AnonymityTypeMapper, args_to_params
import multiprocessing

# Argument parser setup
parser = argparse.ArgumentParser(description='Parse proxies from https://hidemy.name/')
parser.add_argument('file', help='File path for saving proxies')
parser.add_argument('-t', '--types', nargs='+', dest='type', choices=['http', 'https', 'socks4', 'socks5'],
                    help='Proxies\' types list (http, https, socks4 and/or socks5)', default='hs',
                    metavar='http, https, socks4, socks5', action=ProxyTypeMapper)
parser.add_argument('-a', '--anon', nargs='+', dest='anon', choices=['high', 'avg', 'low'],
                    help='Proxy anonymity scale (high, avg, low)', metavar='high, avg, low', action=AnonymityTypeMapper)
parser.add_argument('-p', '--ports', nargs='+', dest='ports', help='Proxies ports')
parser.add_argument('-v', '--validate', help='Invalid proxies will be skipped', action='store_true')
parser.add_argument('-T', '--timeout', '--time', type=int, default=2,
                    help='Max time for validating a proxy. Not needed if -v (validate) flag is not specified.')
parser.add_argument('-l', '--logging', type=str,
                    help='Path to save a logging file. If not specified the logging file won\'t be created.')

args = parser.parse_args().__dict__

logging_file = args.pop('logging')

# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)

if logging_file:
    file_handler = logging.FileHandler(logging_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


filename = args.pop('file')
to_validate = args.pop('validate')
timeout = args.pop('timeout')

params = args_to_params(args)

base_url = 'https://hidemy.name'
base_uri = base_url + '/en/proxy-list/' + params

next_page = base_uri


def get_proxies(html):
    proxies_html = soup.find('tbody').find_all('tr')
    proxies_list = []

    for proxy_html in proxies_html:
        ip = proxy_html.find_next('td')
        port = ip.find_next_sibling()
        types = port.find_all_next('td')[2]

        proxy = Proxy(ip.text, port.text, types.text)

        proxies_list.append(proxy)

        if not to_validate:
            logger.info(f'{proxy.type.name} proxy has been successfully parsed {proxy}')

    if to_validate:
        proxies_list = validate_proxies(proxies_list)

    return proxies_list


def get_next_page(html):
    last_button = soup.find('div', {'class': 'pagination'}).find('ul').find_all('li')[-1]

    # If last button is the page we are in
    if last_button['class'][0] == 'active':
        return None

    return base_url + last_button.find('a')['href']


def validate_proxies(proxies_list):
    def is_valid(proxy):

        req_proxies = {
            'http': f'{proxy.type}://{proxy}',
            'https': f'{proxy.type}://{proxy}'
        }

        try:
            requests.get('https://icanhazip.com/', proxies=req_proxies, timeout=timeout)

            logger.info(f'{proxy.type.name} proxy {proxy} is valid!')

            valid_proxies.append(proxy)
        except Exception:
            logger.info(f'{proxy.type.name} proxy {proxy} is invalid!')

    valid_proxies = multiprocessing.Manager().list()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(is_valid, proxies_list)

    return valid_proxies


def proxies_to_file(filepath, proxies_list):
    with open(filepath, 'a') as f:
        if len(proxies_list):
            f.write("\n".join(map(lambda p: p.__str__(), proxies_list)) + "\n")


if __name__ == '__main__':
    while next_page:
        response = requests.get(next_page, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'})

        soup = BeautifulSoup(response.text, 'html.parser')

        proxies = get_proxies(soup)

        next_page = get_next_page(soup)

        proxies_to_file(filename, proxies)
