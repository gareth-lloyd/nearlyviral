import requests
import json

class InvalidVideoId(Exception):
    pass

class ApiCallFailed(Exception):
    pass

VIDEO_API_ENDPOINT = 'http://vimeo.com/api/v2/video/%s.json'

def video_data(video_id):
    res = requests.get(VIDEO_API_ENDPOINT % video_id)
    if res.status_code == 200:
        return json.loads(res.content)[0]
    if res.status_code == 404:
        raise InvalidVideoId
    raise ApiCallFailed

