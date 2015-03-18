import json
import re

strays = re.compile("^\[|,\n|]$")
def clean(track_string):
    return re.sub(strays, "", track_string)

def hyphenate(string):
    string_parts = string.split(" ")
    with_hyphens = "-".join(string_parts)
    return with_hyphens

def hyphenate_track(track):
    for sample in track["contains_samples_of"]:
        sample["track_name"] = hyphenate(sample["track_name"])
        sample["artist_name"] = hyphenate(sample["artist_name"])

    for sample in track["sampled_by"]:
        sample["track_name"] = hyphenate(sample["track_name"])
        sample["artist_name"] = hyphenate(sample["artist_name"])
    
    return track

def get_name(track_dict):
    track = track_dict["track"] if "track" in track_dict else track_dict
    return track["track_name"] + ":" + track["artist_name"]

def get_edges(track_dict):
    return track_dict["sampled_by"] + track_dict["contains_samples_of"]

with open("../data/whosampled_processed.json", "r") as source:
    cleaned = (clean(line) for line in source)
    tracks = (json.loads(track) for track in cleaned)
    formatted = (hyphenate_track(track) for track in tracks)
    sorted_formatted = sorted(formatted, reverse=True, key=lambda track: len(get_edges(track)))

    formatted = sorted_formatted[:50]
    # formatted = sorted_formatted

    track_names = []
    links = []
    for track in formatted:
        name = get_name(track)
        track_names.append(name)
        for link in track["sampled_by"]:
            sample_source_name = get_name(link)
            track_names.append(sample_source_name)
            link_dict = {
                "source": sample_source_name,
                "target": name
            }
            links.append(link_dict)

        for link in track["contains_samples_of"]:
            sample_source_name = get_name(link)
            track_names.append(sample_source_name)
            link_dict = {
                "source": name,
                "target": sample_source_name
            }
            links.append(link_dict)

    unique_names = list(set(track_names))
    name_indices = {name:index for index, name in enumerate(unique_names)}

    counter_dict = {name:0 for name in unique_names}

    for link in links:
        source = link["source"]
        target = link["target"]

        counter_dict[source] += 1
        counter_dict[target] += 1

        link["source"] = name_indices[source]
        link["target"] = name_indices[target]

    name_dicts_list = [{"name": name, "count": counter_dict[name]} for name in unique_names]

    graph = {
        "nodes": name_dicts_list,
        "links": links
    }

    with open("../data/whosampled.json", "w") as sink:
        sink.write(json.dumps(graph))
        sink.write("\n")

print "finished\n"
