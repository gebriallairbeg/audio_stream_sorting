import pickle
from contextlib import suppress


MAX_AUTHORS_SONG_INTERVAL = 10
TEMP_TAGS = ['Медленный', 'Средний']
YEAR_TAGS = ['2015-г', '2016-г', '2017']


class MediaStreamStorage(object):
    authors = {}
    media_stream = []
    songs = []

    def __init__(self, no_song_repeation=False):
        '''
        need to be initialized with True if no_song_repeation logic needed
        '''
        self.no_song_repeation = no_song_repeation

    def update_authors(self, author):
        '''
        marks author as already used and re-build all other authors in storage
        '''
        for key in self.authors:
            if key != author or self.authors[key] >= MAX_AUTHORS_SONG_INTERVAL:
                self.authors[key] += 1
        self.authors[author] = 0

    def availability_by_author(self, song):
        '''
        checks is song could be inserted right now
        in addition check for song repeation if enabled
        '''
        return (
            self.authors.get(song['artist_id'], MAX_AUTHORS_SONG_INTERVAL) >= MAX_AUTHORS_SONG_INTERVAL
            and ((song['id'] not in self.songs and self.no_song_repeation) or not self.no_song_repeation))

    def push_song(self, song, efficiency):
        '''
        processing song insertion
        '''
        self.media_stream.append((song['id'], song['title'], efficiency))
        if self.no_song_repeation:
            self.songs.append(song['id'])
        self.update_authors(song['artist_id'])


def get_temp_n_year_sources(tags):
    temps_len, years_len = len(TEMP_TAGS), len(YEAR_TAGS)

    # create another tag source that helps
    # to recognize temp/year tags based on values
    filtered_tags = {}
    for key, value in iter(tags.items()):
        if value in TEMP_TAGS or value in YEAR_TAGS:
            filtered_tags[hash(value)] = key
        if (len(filtered_tags.keys()) == temps_len + years_len):
            break

    # reverse processing from value -> to id
    temps = [filtered_tags[hash(i)] for i in TEMP_TAGS]
    years = [filtered_tags[hash(i)] for i in YEAR_TAGS]
    return temps, temps_len, years, years_len

def main():
    with open('mediafiles.pickle', 'rb') as media_source, open('tags.pickle', 'rb') as tags_source:
        mediafiles = pickle.load(media_source)
        tags = pickle.load(tags_source)

        temp_tags, temps_len, year_tags, year_len = get_temp_n_year_sources(tags)
        rules_length = len(mediafiles)

        # here we obtain a sequence of temps and years mixed in accordance with requirement 2
        # I use len(mediafiles) as limiter, because for some cases there may be infinit output line
        # (when the sequence of a/b rules begins to repeat too often with relation to the length of the content)
        rules_sets = ((temp_tags[i % temps_len], year_tags[i % year_len]) for i in range(rules_length))
        stream = MediaStreamStorage()

        for (temp, year) in rules_sets:

            # checks are made in the form of generators
            # because we choose the first convenient track
            # NO upward strategy, linear search only
            CONDITIONS = [
                ((True, True, True), (song for song in mediafiles if (
                    stream.availability_by_author(song) and temp in song['tags'] and year in song['tags']))),

                ((True, True, False), (song for song in mediafiles if (
                    stream.availability_by_author(song) and temp in song['tags'] and year not in song['tags']))),

                ((True, False, True), (song for song in mediafiles if (
                    stream.availability_by_author(song) and temp not in song['tags'] and year in song['tags']))),

                ((True, False, False), (song for song in mediafiles if (
                    stream.availability_by_author(song) and not (temp in song['tags'] or year in song['tags'])))),

                ((False, True, True), (song for song in mediafiles if (
                    not stream.availability_by_author(song) and temp in song['tags'] and year in song['tags']))),

                ((False, True, False), (song for song in mediafiles if (
                    not stream.availability_by_author(song) and temp in song['tags'] and year not in song['tags']))),

                ((False, False, True), (song for song in mediafiles if (
                    not stream.availability_by_author(song) and temp not in song['tags'] and year in song['tags']))),

                ((False, False, False), (song for song in mediafiles if (
                    not (stream.availability_by_author(song) or temp in song['tags'] or year in song['tags'])))),
            ]

            for condition in CONDITIONS:
                with suppress(StopIteration):
                    stream.push_song(next(condition[1]), condition[0])
                    break

    with open('output.pickle', 'wb') as f:
        pickle._dump(stream.media_stream, f)


if __name__ == '__main__':
    main()


