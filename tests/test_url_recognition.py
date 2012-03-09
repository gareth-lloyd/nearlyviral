from unittest import TestCase
from watchlinks.analyze import vid_identifier

TEST_DATA = {
    'http://www.youtube.com/watch?v=hztjXWFUgA4': 'hztjXWFUgA4',
    'http://youtu.be/5IaYm8sUVWA?a': '5IaYm8sUVWA',
    'http://youtu.be/5IaYm8sUVWA': '5IaYm8sUVWA',
    'http://www.youtube.com/watch?feature=player_embedded&v=2Rql00Fixz4#': '2Rql00Fixz4',
    'http://www.youtube.com/watch?v=4OYn2Bq4OJY&=mtkz': '4OYn2Bq4OJY',

    'http://m.youtube.com/#/profile?user=YBMFilmz&view=videos&v=H18De2yKjf4': 'H18De2yKjf4',
    'http://m.youtube.com/watch?v=olanYwPrgn0': 'olanYwPrgn0',
    'http://m.youtube.com/index?desktop_uri=%2F&gl=BR#/watch?v=cMCIOaFfavs': 'cMCIOaFfavs',
    'http://www.youtube.com/v/Mnt0Iwemy0A': 'Mnt0Iwemy0A',
    'http://www.youtube.com/v/mgCIKGIYJ1A?hl=en': 'mgCIKGIYJ1A',
    'http://www.youtube.com/user/TsunamiDopeHouse/videos': False,
    'http://www.youtube.com/commercialmusicgroup': False,
    'http://www.youtube.com/': False,


    'https://vimeo.com/38221464': '38221464',
    'http://www.vimeo.com/38221464': '38221464',
    'http://vimeo.com/m/37119711': '37119711',
    'http://vimeo.com/user7091956/garryclarksonnewport': False,
    'http://www.vimeo.com/vamp/leon': False,
    'http://vimeo.com/invisible/kony2012': False,

    'http://adf.ly/68t3C': False,
    None: False,
    'http': False,
}
class UrlRecognitionTests(TestCase):

    def test_vid_identifier(self):
        def test(url_id):
            url, identifier = url_id[0], url_id[1]
            self.assertEquals(identifier, vid_identifier(url))

        map(test, TEST_DATA.iteritems())
