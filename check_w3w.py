import requests
examples = [
    'engrossed.primaries.barbecued',
    '///engrossed.primaries.barbecued',
    'index.home.raft',
    '///index.home.raft',
    'filled.count.soap',
    '///filled.count.soap',
]
for q in examples:
    r = requests.get('https://nominatim.openstreetmap.org/search',
                     params={'q': q, 'format': 'json', 'limit': 1},
                     headers={'User-Agent': 'coffee-finder-app'})
    print('query', q, '->', r.status_code, r.text)
