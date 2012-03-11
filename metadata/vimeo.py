import requests
import json

VIDEO_API_ENDPOINT = 'http://vimeo.com/api/v2/video/%s.json'

def video_data(video_id):
    res = requests.get(VIDEO_API_ENDPOINT % video_id)
    return json.loads(res.content)
