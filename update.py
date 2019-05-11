import json
from collections import defaultdict
from itertools import cycle
from pathlib import Path
import os
import sys

import requests

moon = cycle('🌑🌒🌓🌔🌕🌖🌗🌘')


def parse_int(s):
    try:
        return int(s)
    except ValueError as e:
        return -1


def get_wd_id(s):
    url = f'https://www.wikidata.org/w/api.php?action=wbsearchentities&search={s}&format=json&language=en&uselang=en&type=item'
    r = requests.get(url)

    for wd_id in [x['title'] for x in r.json()['search']]:
        url = f'https://www.wikidata.org/wiki/Special:EntityData/{wd_id}.json'

        r = requests.get(url)
        try:

            if r.json()['entities'][wd_id]['claims']['P31'][0]['mainsnak']['datavalue']['value']['id'] in (
            'Q5398426', 'Q581714', 'Q1259759', 'Q15416'):
                return wd_id
        except:
            print(f'something wrong with {s} [{wd_id}]')

    return input("Wikidata ID: ")


def get_wd_object(wd_id):
    r = requests.get(f'https://www.wikidata.org/wiki/Special:EntityData/{wd_id}.json')
    return r.json()

def get_type(wd_id, wd_object):
    try:
        return wd_object['entities'][wd_id]['claims']['P31'][0]['mainsnak']['datavalue']['value']['id']
    except:
        return None

def get_title(wd_id, wd_object):
    labels = wd_object['entities'][wd_id]['labels']
    if 'en' in labels:
        return labels['en']['value']
    if 'de' in labels:
        return labels['de']['value']


def get_no_of_seasons(wd_id, wd_object):
    try:
        return int(wd_object['entities'][wd_id]['claims']['P2437'][0]['mainsnak']['datavalue']['value']['amount'])
    except:
        return None


def get_imdb_id(wd_object):
    if 'P345' not in wd_object['entities'][wd_id]['claims']:
        return None

    return wd_object['entities'][wd_id]['claims']['P345'][0]['mainsnak']['datavalue']['value']


def get_imdb_rating(imdb_id):
    from requests_html import HTMLSession
    session = HTMLSession()
    r = session.get(f'https://www.imdb.com/title/{imdb_id}/')
    try:
        return float(r.html.find('.ratingValue span')[0].text)
    except:
        return None


if __name__ == '__main__':

    root_dir = Path(sys.argv[1])

    # read index-file
    shows = defaultdict(dict)
    if Path('index.json').exists():
        with open('index.json', 'r') as f:
            shows = defaultdict(dict, json.load(f))

    # update last_downloaded counter
    for show in sorted([x for x in root_dir.iterdir() if x.is_dir()]):
        print(f'{next(moon)} {show.name:<50} ', end='')

        if shows.get(show.name, {}).get('skip', False):
            print()
            continue

        shows[show.name]['last_downloaded'] = max([parse_int(x.name) for x in show.iterdir() if x.is_dir()])

        if shows[show.name].get("wd_id") is None:
            wd_id = get_wd_id(show.name)
            if wd_id == 'skip' or len(wd_id) == 0:
                shows[show.name]['skip'] = True
                continue
            shows[show.name]["wd_id"] = wd_id
        wd_id = shows[show.name]["wd_id"]

        wd_object = get_wd_object(wd_id)

        shows[show.name]['last_season_available'] = get_no_of_seasons(wd_id, wd_object)
        shows[show.name]['wd_title'] = get_title(wd_id, wd_object)
        shows[show.name]['wd_type'] = get_type(wd_id, wd_object)

        imdb_id = get_imdb_id(wd_object)
        shows[show.name]['imdb_id'] = imdb_id
        shows[show.name]['imdb_rating'] = get_imdb_rating(imdb_id)

        # print(json.dumps(shows[show.name], indent=2))

        # save changes
        with open('index.json.new', 'w') as f:
            json.dump(shows, f, indent=2, sort_keys=True)
        os.rename("index.json.new", "index.json")

        print(f'{shows[show.name]["wd_title"]}')

    # save changes
    with open('index.json.new', 'w') as f:
        json.dump(shows, f, indent=2, sort_keys=True)
    os.rename("index.json.new", "index.json")
