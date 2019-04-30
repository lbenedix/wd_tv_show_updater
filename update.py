import json
from pathlib import Path
import os
import sys

import requests


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
            if r.json()['entities'][wd_id]['claims']['P31'][0]['mainsnak']['datavalue']['value']['id'] == 'Q5398426':
                return wd_id
        except:
            print(f'something wrong with {s} [{wd_id}]')

    return input("Wikidata ID: ")


def get_wd_object(wd_id):
    r = requests.get(f'https://www.wikidata.org/wiki/Special:EntityData/{wd_id}.json')
    return r.json()


def get_no_of_seasons(wd_object):
    return int(wd_object['entities'][wd_id]['claims']['P2437'][0]['mainsnak']['datavalue']['value']['amount'])


def get_imdb_id(wd_object):
    if 'P345' not in wd_object['entities'][wd_id]['claims']:
        return None

    return wd_object['entities'][wd_id]['claims']['P345'][0]['mainsnak']['datavalue']['value']


if __name__ == '__main__':

    root_dir = Path(sys.argv[1])

    # read index-file
    with open('index.json', 'r') as f:
        shows = json.load(f)

    # update last_downloaded counter
    for show in [x for x in root_dir.iterdir() if x.is_dir()]:
        print(show.name)

        if shows[show.name].get('skip', False):
            continue

        shows[show.name]['last_downloaded'] = max([parse_int(x.name) for x in show.iterdir() if x.is_dir()])

        if shows[show.name]["wd_id"] is None:
            shows[show.name]["wd_id"] = get_wd_id(show.name)
        wd_id = shows[show.name]["wd_id"]

        wd_object = get_wd_object(wd_id)
        shows[show.name]['last_season_available'] = get_no_of_seasons(wd_object)
        shows[show.name]['imdb_id'] = get_imdb_id(wd_object)

        # print(json.dumps(shows[show.name], indent=2))

        if shows[show.name]['last_season_available'] is None:
            print('.')

        # save changes
        with open('index.json.new', 'w') as f:
            json.dump(shows, f, indent=2, sort_keys=True)
        os.rename("index.json.new", "index.json")
