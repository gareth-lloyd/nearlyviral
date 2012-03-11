from unittest import TestCase
from watchlinks.analyze import vimeo_id

TEST_DATA = {
    'https://vimeo.com/38221464': '38221464',
    'http://www.vimeo.com/38221464': '38221464',
    'http://vimeo.com/m/37119711': '37119711',
    'http://vimeo.com/user7091956/garryclarksonnewport': False,
    'http://www.vimeo.com/vamp/leon': False,
    'http://vimeo.com/invisible/kony2012': False,
    'http://vimeo.com/hd#37848135': '37848135',
    'http://player.vimeo.com/video/37119711?title=0&byline=0&portrait=0&color=d13030&quot': '37119711',

    'http://adf.ly/68t3C': False,
    None: False,
    'http': False,
}
class UrlRecognitionTests(TestCase):

    def test_vid_identifier(self):
        def test(url_id):
            url, identifier = url_id[0], url_id[1]
            self.assertEquals(identifier, vimeo_id(url))

        map(test, TEST_DATA.iteritems())
