import os
import sys
import json
import argparse
from unicodedata import normalize
from tqdm import tqdm

from app.search import create_index
from django.conf import settings


def main(args):

    parser = argparse.ArgumentParser()

    parser.add_argument("-r", "--root_path", nargs='?', help="Root text path")
    parser.add_argument("-f", "--html_path", nargs='?', help="Html formatting path")


    args = parser.parse_args(args)

    root_path = args.root_path or f'../sc-data/segmented_data/root/pli/ms/sutta/mn/'
    html_path = args.html_path or f'../sc-data/segmented_data/html/pli/ms/sutta/mn/'

    (_, _, file_names) = next(os.walk(root_path))

    file_names = [f'mn{i}_root-pli-ms.json' for i in range(1, 11)]

    text_dict = {}

    for file_name in tqdm(file_names, desc='Formatting HTML text'):

        try:
            file_name_stub = file_name.split('_')[0]
            with open(os.path.join(root_path, file_name), 'r') as f:
                root = json.load(f)
            with open(os.path.join(html_path, f'{file_name_stub}_html.json'), 'r') as f:
                html = json.load(f) 

            text = ''
            for key, value in html.items():
                if key.split(':')[1] == '0.1':
                    division = root[key]
                elif key.split(':')[1] == '0.2':
                    sutta_title = root[key]
                text += value.replace('{}', root[key])

            text_dict[f'{division} - {sutta_title}'] = normalize('NFKC', text)

        except KeyError:
            print(f'{file_name} could not be formatted')

    create_index(settings.INDEX_DIR, text_dict)

if __name__ == '__main__':
    main(sys.argv[1:])
