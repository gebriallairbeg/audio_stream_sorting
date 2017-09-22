
script that sorts the list of media lines according to the rules
  1: there must be at least 10 tracks between tracks of one artist;
  2: tracks must match two patterns: 
    - alternation of rates and years (Медленный, Средний, '2015-d', '2016-g', '2017'))
    Thus, the first track should have the tags 'Медленный' (id tag 17) and '2015' (id tag 31658), Third - 'Медленный' (17) and '2017' (32531), Fourth - 'Средний' (16) and '2015' (31658) and so on to the end. If a track is not found for a specific position, we add to the sequence any of the remaining items. The result should be a list in the format
