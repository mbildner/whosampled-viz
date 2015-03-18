import requests
from pyquery import PyQuery as pq
import json

def hyphenate(string):
	split_up = string.split(" ")
	joined = "-".join(split_up)
	return joined

def crawl(track_dict):
	artist_name = hyphenate(track_dict["artist_name"])
	track_name = hyphenate(track_dict["track_name"])

	# get tracks that this track samples
	url = "http://www.whosampled.com/{artist_name}/{track_name}".format(artist_name=artist_name, track_name=track_name)
	track_page = pq(requests.get(url).text)

	has_contains_samples = track_page("#content > div.leftContent > div.innerContent > div:nth-child(1) > span").text().startswith("Contains")
	has_sampled_by = track_page("#content > div.leftContent > div.innerContent > div:nth-child(3) > span").text().startswith("Was sampled")

	contains_samples = track_page("#content > div.leftContent > div.innerContent > ul:nth-child(2) > li > span")
	contains_samples_of = []
	for track in contains_samples:
		anchors = pq(track).find("a")

		year = pq(track).find("span.trackArtist").text()[-5:-1]

		track_dict = {
			"artist_name": anchors[1].text,
			"track_name": anchors[0].text,
			"year": year
		}

		contains_samples_of.append(track_dict)


	contains_sampled_by = []
	if has_sampled_by == True:
		# get tracks that sample this track
		has_sampled_page = len(track_page("#content > div.leftContent > div.innerContent > div:nth-child(3) > a")) == 1

		if has_sampled_page == True:
			sampled_url = url + "/sampled"
			track_page = pq(requests.get(sampled_url).text);

		sampled_by = track_page("#content > div.leftContent > div.innerContent > ul > li > span")

		for track in sampled_by:
			anchors = pq(track).find("a")

			year = pq(track).find("span.trackArtist").text()[-5:-1]

			track_dict = {
				"artist_name": anchors[1].text,
				"track_name": anchors[0].text,
				"year": year
			}

			contains_sampled_by.append(track_dict)

	samples_lists_dict = {
		"track": {
			"track_name": track_name,
			"artist_name": artist_name
		},
		"contains_samples_of" : contains_samples_of,
		"sampled_by": contains_sampled_by
	}

	return samples_lists_dict


def store(item, f):
	print "storing ", item
	f.write(json.dumps(item))
	f.write("\n")

def get_hash(track):
	return track["track_name"] + track["artist_name"]


def crawl_until(seed, limit=100000):
	with open("whosampled.json", "a") as sink:
		counter = 0
		holder = seed[:]
		# seen = set()

		while counter < limit:
			track = holder.pop(0)

			try:
				result = crawl(track)
				print result
				store(result, sink)
				edges = result["contains_samples_of"] + result["sampled_by"]

				holder += edges
				# seen.add(get_hash(result["track"]))
				counter += 1

			except:
				pass

		# finish up the list
		for track in holder:
			try:
				store(holder, sink)
			except:
				pass

seed_track_list = [
	{"track_name": "Baptizing-Scene", "artist_name": "Reverend-W.A.-Donaldson"},
	{"track_name": "Victory", "artist_name": "Puff-Daddy"},
	{"track_name": "The-One", "artist_name": "Kanye-West"},
	{"track_name": "All-Day", "artist_name": "Kanye-West"},
	{"track_name": "Nightmare-on-Figg-St.", "artist_name": "ScHoolboy-Q"},
	{"track_name": "Let-Me-Go-in-Paris", "artist_name": "Marsha-Ambrosius"}
]

crawl_until(seed_track_list)
