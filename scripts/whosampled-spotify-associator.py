import requests
import json

uri_template = "http://ws.spotify.com/search/1/track.json?q={track}+artist:{artist}"

def get_uri(track, artist):
    return uri_template.format(track=(track.encode("ascii", "ignore")), artist=(artist.encode("ascii", "ignore")))

with open("../data/whosampled.json", "r") as source:
    graph = json.load(source)
    nodes = graph["nodes"]
    names = [node["name"].split(":") for node in nodes]

    for name in names[0:2]:
        artist = name[0]
        track = name[1]

        result = requests.get(get_uri(track, artist))
        print result.text


