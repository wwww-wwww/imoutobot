from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import io
import requests
import json

class ImageUploadError(Exception):
    def __init__(self, message):
        super().__init__(message)

def upload(imgdata):
    resp = requests.post(
        "https://f.okea.moe/api/upload",
        files={'file' : ('1.png', imgdata)})

    #if resp.ok and resp.text != None and "https://a.uguu.se" in resp.text:
        #return resp.text

    resp_json = resp.json()

    if resp.ok and resp_json and resp_json["success"] == True and resp_json["url"] != None:
        return resp_json["url"]

    #if resp.ok and resp.json() and resp.json()["success"] and resp.json()["file"] != None:
    #    return resp.json()["file"][0]["url"]
    raise ImageUploadError("Unexpected pomf response: HTTP Status: {} \nOutput: {}".format(resp.status_code, resp.text))

class Txt2Img:
    def __init__(self):
        self.font = ImageFont.truetype("arial.ttf", 15)

    def create_img(self, text, diff=True):
        w = 0
        for a in text:
            tw = self.font.getsize(a)[0]
            if tw > w:
                w = tw

        w += 4

        h = len(text) * 19
        img = Image.new('RGBA', (w, h))

        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, w, h], fill=(255, 255, 255))

        for k, v in enumerate(text):
            if diff and len(v) > 0:
                if v[0] == '-':
                    d.rectangle([0, k * 19, w, k * 19 + 19], fill=(255, 230, 230))
                elif v[0] == "+":
                    d.rectangle([0, k * 19, w, k * 19 + 19], fill=(220, 255, 220))
            d.text((2, 2 + k * 19), v, font=self.font, fill=(0, 0, 0))

        s = io.BytesIO()
        img.convert(mode="P").save(s, format='png', optimize=True)
        return upload(s.getvalue())
