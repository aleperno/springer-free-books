import wget
import os
import requests
import time

from pandas import read_excel
from tqdm import tqdm
from multiprocessing.pool import ThreadPool
from multiprocessing import Lock, Value, Array
from argparse import ArgumentParser
from functools import partial
from urllib.error import HTTPError


CATALOG_URL = "https://resource-cms.springernature.com/springer-cms/rest/v1/content/17858272/data/v4"
CATALOG_FILE = "Springer Free Books Catalog.xlsx"
DOWNLOAD_FOLDER = "downloads"


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('-n', '--number', help='Number of threads (Default 1)', type=int, default=1)
    return parser.parse_args()


def get_available(array, lock):
    with lock:
        while True:
            for e, available in enumerate(array):
                if available:
                    array[e] = False
                    return e


def release_pos(array, lock, pos):
    with lock:
        array[pos] = True


def check_catalog_file():
    if not os.path.exists(CATALOG_FILE):
        print("Downloading catalog file")
        wget.download(CATALOG_URL, CATALOG_FILE)
        print()
        print(f"Catalog File save at {CATALOG_FILE}")
        print("The script will download ALL the books in the given file")
        print("Delete the unwanted files or leave it as it is")
        input("Press ENTER to continue")


def read_catalog():
    return read_excel(CATALOG_FILE)[['OpenURL', 'Book Title', 'Author', 'English Package Name', 'Print ISBN']].values


def bar_aux(current, total, width, pbar):
    pbar.total = total
    pbar.update(current - pbar.n)


def download_book(args):
    data, array, lock = args
    url, title, author, category, isbn = data

    folder = os.path.join(DOWNLOAD_FOLDER, category)

    if not os.path.exists(folder):
        try:
            os.mkdir(folder)
        except FileExistsError:
            pass

    new_url = requests.get(url).url

    base_file_name = f"{title} - {author} - {isbn}"
    # File cannot contain '/', makes wget fail
    base_file_name = base_file_name.replace('/', '-')
    base_file = os.path.join(folder, base_file_name)

    pdf_download_url = new_url.replace('book', 'content/pdf') + '.pdf'
    pdf_output_file = base_file + '.pdf'

    epub_download_url = new_url.replace('book', 'download/epub') + '.epub'
    epub_output_file = base_file + '.epub'

    position = get_available(array, lock)

    for output_file, download_url in ((pdf_output_file, pdf_download_url), (epub_output_file, epub_download_url)):

        if os.path.exists(output_file):
            # We have already downloaded the file
            continue
        else:
            try:
                with tqdm(total=100, leave=False, position=position + 1, desc=title[:30].ljust(30)) as pbar:
                    mybar = partial(bar_aux, pbar=pbar)
                    wget.download(download_url, output_file, bar=mybar)
            except HTTPError:
                pass

    release_pos(array, lock, position)


def download_books(threads=1):
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.mkdir(DOWNLOAD_FOLDER)

    array = Array('i', [True for i in range(threads)])
    lock = Lock()

    catalog = read_catalog()
    catalog_size = len(catalog)

    with ThreadPool(threads) as p:
        args = [(book_data, array, lock) for book_data in catalog]

        for _ in tqdm(p.imap_unordered(download_book, args), desc='GLOBAL', position=0, total=catalog_size):
            pass


def main():
    args = parse_args()
    threads = args.number
    check_catalog_file()
    download_books(threads)


if __name__ == '__main__':
    main()
