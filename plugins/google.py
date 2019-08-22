from disco.bot import Plugin
from disco.types.message import MessageEmbed
import config as cfg
import random, re, requests, urllib.request, urllib.parse

class Google(Plugin):

    def load(self, ctx):
        super(Google, self).load(ctx)

        self.category = "Searches"
        self.cmds = {}
        self.cmds["google"] = ["!google <query> !g <query>", "Search Google"]
        self.cmds["googleimages"] = ["!googleimages <query> !googlei <query> !g <query>", "Search Google images"]
        self.cmds["youtube"] = ["!youtube <query> !yt <query>", "Search YouTube for a video"]

    @Plugin.command('google', '<search:str...>')
    @Plugin.command('g', '<search:str...>')
    def on_google(self, event, search):
        
        r = requests.get("https://www.googleapis.com/customsearch/v1",
            params = {
                "key": cfg.google_key,
                "cx": cfg.google_cx,
                "q": search
                })

        if len(r.content) > 0 and len(r.json()) > 0 and "items" in r.json() and len(r.json()["items"]) > 0:

            item = r.json()["items"][0]

            embed = MessageEmbed()
            embed.color = cfg.color
            embed.title = item["title"]
            embed.url = item["link"]
            embed.description = item["snippet"]

            event.msg.reply('', embed=embed)
        
        else:
            event.msg.reply("nothing found")
    
    @Plugin.command('googleimages', '<search:str...>')
    @Plugin.command('googlei', '<search:str...>')
    @Plugin.command('gi','<search:str...>')
    def on_google_i(self, event, search):

        r = requests.get("https://www.googleapis.com/customsearch/v1",
            params = {
                "key": cfg.google_key,
                "cx": cfg.google_cx,
                "searchType": "image",
                "q": search
                })

        if len(r.content) > 0 and len(r.json()) > 0 and "items" in r.json() and len(r.json()["items"]) > 0:

            item = r.json()["items"][random.randint(0, len(r.json()["items"]) - 1)]

            embed = MessageEmbed()
            embed.color = cfg.color
            embed.title = search

            if "link" in item:
                embed.set_image(url=item["link"])
                event.msg.reply('', embed=embed)

        else:
            event.msg.reply("nothing found")

    @Plugin.command('youtube', '<content:str...>')
    @Plugin.command('yt', '<content:str...>')
    def on_yt(self, event, content):

        query_string = urllib.parse.urlencode({"search_query" : content})
        html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)

        search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
        
        if len(search_results) > 0:
            event.msg.reply("http://www.youtube.com/watch?v=" + search_results[0])
        else:
            event.msg.reply("nothing found")
            