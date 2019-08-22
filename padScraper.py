import json
import config as cfg

# Get pad text
def get_pad_text(s, pad_id):
    url = cfg.api_url + "getText"
    r = s.get(url, params={"apikey":cfg.api_key, "padID":pad_id})
    return r.json()["data"]["text"]

# Get song list (json)
def get_songlist():
    return json.load(open(cfg.songlist_path, encoding='utf-8'))

# Get sheets (json)
def get_sheets():
    return json.load(open(cfg.sheets_path, encoding='utf-8'))
