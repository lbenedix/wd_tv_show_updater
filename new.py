import json

with open('index.json', 'r') as f:
    shows = json.load(f)


for show in shows:
    try:
        if shows[show].get('last_downloaded') < shows[show].get('last_season_available'):
            print(show)
            print(json.dumps(shows[show], indent=2))
            print()
    except:
        print('??? ', show)
