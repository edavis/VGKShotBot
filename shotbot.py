#!/usr/bin/env python

import time
import logging
import requests
import datetime
import jsonpatch

REFRESH_INTERVAL = 10

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s'
)

def main():
    pbp_url = 'http://statsapi.web.nhl.com/api/v1/game/2019020171/feed/live/diffPatch'
    end_timecode = datetime.datetime(2019, 10, 27, 21, 07, 00)
    pbp_url_params = {'endTimecode': end_timecode.strftime('%Y%m%d_%H%M%S')}
    pbp_doc = requests.get(pbp_url, params=pbp_url_params).json()

    start_timecode = pbp_doc['metaData']['timeStamp']
    time.sleep(REFRESH_INTERVAL)

    while True:
        end_timecode += datetime.timedelta(seconds=30)
        pbp_url_params = {
            'startTimecode': start_timecode,
            'endTimecode': end_timecode.strftime('%Y%m%d_%H%M%S'),
        }
        pbp_diff = requests.get(pbp_url, params=pbp_url_params).json()

        if not pbp_diff:
            logging.debug('JSON diff returned? No')
            time.sleep(REFRESH_INTERVAL)
            continue
        else:
            logging.debug('JSON diff returned? Yes')

        for diff_wrapper in pbp_diff:
            patch = jsonpatch.JsonPatch(diff_wrapper['diff'])
            pbp_doc = patch.apply(pbp_doc, in_place=True) # in_place? yes? no?

        pbp_num_plays = len(pbp_doc['liveData']['plays']['allPlays'])

        logging.debug('Number of plays in PBP: %d' % pbp_num_plays)

        currentPlay = pbp_doc['liveData']['plays']['currentPlay']
        logging.debug('Current play: %r' % currentPlay['result']['description'])

        start_timecode = pbp_doc['metaData']['timeStamp']

        print
        time.sleep(REFRESH_INTERVAL)

if __name__ == '__main__':
    main()
