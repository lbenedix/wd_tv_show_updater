import json

with open('index.json', 'r') as f:
    shows = json.load(f)

counter = 0
u_counter = 0
sum = 0
not_completed = []
for show in shows:
    counter += 1
    try:
        downloaded = shows[show].get('last_downloaded')
        available = shows[show].get('last_season_available')
        wd_id = shows[show].get('wd_id')

        if  downloaded < available:
            not_completed.append(show)
            print(f'{show:<40} {downloaded:>2} / {available:>2} https://www.wikidata.org/wiki/{wd_id}')
            # print(json.dumps(shows[show], indent=2))
            u_counter += 1
            sum += shows[show].get('last_season_available') - shows[show].get('last_downloaded')
    except:
        pass


print(f'{u_counter}/{counter} ({sum})')
