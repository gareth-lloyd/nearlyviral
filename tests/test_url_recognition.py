from unittest import TestCase
from gather.process_links import parse_vimeo_url, NonVimeoUrl

TEST_DATA = {
    '/38221464': '38221464',
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
            url, vimeo_id= url_id[0], url_id[1]
            if not vimeo_id:
                self.assertRaises(NonVimeoUrl, parse_vimeo_url, url)
            else:
                self.assertEquals(vimeo_id, parse_vimeo_url(url))

        map(test, TEST_DATA.iteritems())
