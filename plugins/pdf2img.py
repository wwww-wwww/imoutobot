from disco.bot import Plugin
from disco.types.message import MessageEmbed
from pdf2image import convert_from_bytes
import config as cfg
import requests, io, re, urllib.parse
import plugins.paginator as paginator

class Pdf2Img(Plugin):

    def load(self, ctx):
        super(Pdf2Img, self).load(ctx)
        self.category = "Util."
        self.cmds = {}
        self.cmds["pdf"] = ["!pdf <url>", "Embed a pdf"]

    @Plugin.command('pdf', '<content:str...>')
    def on_pdf(self, event, content):
        
        r = requests.get(content, allow_redirects=True)

        pages = convert_from_bytes(r.content)

        images = []

        for image in pages:
            s = io.BytesIO()
            image.convert(mode="P").save(s, format='png')
            images.append({"path": None, "data": s.getvalue()})

        embed = MessageEmbed()
        embed.color = cfg.color
        
        fname = ''
        if "Content-Disposition" in r.headers.keys():
            fname = re.findall("filename=(.+)", r.headers["Content-Disposition"])[0]
        else:
            fname = content.split("/")[-1]

        embed.title = urllib.parse.unquote(fname)

        paginator.create_images(self, embed, images, event.msg.reply)
