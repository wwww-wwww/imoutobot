from disco.bot import Plugin
from disco.types.message import MessageEmbed
import config as cfg
import random, requests
from util.storage import Storage

class Danbooru(Plugin):

    def load(self, ctx):
        super(Danbooru, self).load(ctx)

        self.category = "Searches"
        self.cmds = {}
        self.cmds["danbooru"] = ["!danbooru <tag> !danbooru <tag>+<tag>", "Search Danbooru for specified tags"]
        self.cmds["gelbooru"] = ["!gelbooru <tag> !gelbooru <tag>+<tag>", "Search Gelbooru for specified tags"]
        self.cmds["setwaifu"] = ["!setwaifu <tag>", "Set your waifu with danbooru tags"]
        self.cmds["mywaifu"] = ["mywaifu", "Get a random image of your saved tag on danbooru"]
        self.cmds["mywaifux"] = ["mywaifux", "Get a random image of your saved tag on danbooru. Safe tag off"]

        self.waifus = Storage("waifus.json")

    @Plugin.command('danbooru', '<tags:str...>')
    def on_danbooru(self, event, tags):
        
        count = requests.get("https://danbooru.donmai.us/counts/posts.json",
            params = {
                "tags": tags
            })

        if len(count.content) > 0 and len(count.json()) > 0 and "counts" in count.json() and "posts" in count.json()["counts"]:
            count = count.json()["counts"]["posts"]
                
        r = requests.get("https://danbooru.donmai.us/posts.json", 
            params = {
                "tags": tags, 
                "limit": 200,
                "random": "true" if count > 200 else "false"
                })

        if len(r.content) > 0 and len(r.json()) > 0:
            if "success" in r.json() and not r.json()["success"]:
                event.message.reply(r.json()["message"])
                return

            n = random.randint(0, len(r.json()) - 1)

            embed = MessageEmbed()
            embed.color = cfg.color
            embed.title = tags
            embed.url = "https://danbooru.donmai.us/posts/{}".format(r.json()[n]["id"])

            if "large_file_url" in r.json()[n]:
                embed.set_image(url=r.json()[n]["large_file_url"])
            else:
                embed.set_image(url=r.json()[n]["file_url"])

            event.msg.reply('', embed=embed)
        
        else:
            event.msg.reply("nothing found")

    @Plugin.command('gelbooru', '<tags:str...>')
    def on_gelbooru(self, event, tags):

        r = requests.get("https://gelbooru.com/index.php", 
            params = {
                "page": "dapi",
                "s": "post",
                "q": "index",
                "tags": tags,
                "limit": 200,
                "json": 1
                })

        if len(r.content) > 0 and len(r.json()) > 0:

            n = random.randint(0, len(r.json()) - 1)

            embed = MessageEmbed()
            embed.color = cfg.color
            embed.title = tags
            embed.url = "https://gelbooru.com/index.php?page=post&s=view&id={}".format(r.json()[n]["id"])

            embed.set_image(url=r.json()[n]["file_url"])

            event.msg.reply("", embed=embed)
        
        else:
            event.msg.reply("nothing found")

    @Plugin.command('setwaifu', '<tags:str...>')
    def on_setwaifu(self, event, tags):
        if len(tags) > 0:
            self.waifus[str(event.msg.author.id)] = tags
            event.msg.reply("waifu set")

    @Plugin.listen('MessageCreate')
    def on_mywaifu(self, event):
        if event.message.content.lower() == "mywaifu" or event.message.content.lower() == "mywaifux":
            key = str(event.author.id)
            if key in self.waifus:
            
                count = requests.get("https://danbooru.donmai.us/counts/posts.json",
                    params = {
                        "tags": self.waifus[key] + (" rating:safe" if event.message.content.lower() == "mywaifu" else ""), 
                        })

                if len(count.content) > 0 and len(count.json()) > 0 and "counts" in count.json() and "posts" in count.json()["counts"]:
                    count = count.json()["counts"]["posts"]

                r = requests.get("https://danbooru.donmai.us/posts.json", 
                    params = {
                        "tags": self.waifus[key] + (" rating:safe" if event.message.content.lower() == "mywaifu" else ""), 
                        "limit": 200,
                        "random": "true" if count > 200 else "false"
                        })
                
                if len(r.content) > 0 and len(r.json()) > 0:
                    if "success" in r.json() and not r.json()["success"]:
                        event.message.reply(r.json()["message"])
                        return

                    n = random.randint(0, len(r.json()) - 1)

                    embed = MessageEmbed()
                    embed.color = cfg.color
                    embed.url = "https://danbooru.donmai.us/posts/{}".format(r.json()[n]["id"])

                    if "large_file_url" in r.json()[n]:
                        embed.set_image(url=r.json()[n]["large_file_url"])
                    else:
                        embed.set_image(url=r.json()[n]["file_url"])
                    embed.set_footer(text=r.json()[n]["id"])

                    event.message.reply('', embed=embed)
                
                else:
                    event.message.reply("nothing found")
            else:
                event.message.reply("waifu not set. use !setwaifu danbooru_tag")


    @Plugin.command('dab')
    def on_dab(self, event):

        r = requests.get("https://danbooru.donmai.us/posts.json", 
            params = {
                "tags": "dab_(dance) rating:safe", 
                "limit": 200,
                "random": "false"
                })

        if len(r.content) > 0 and len(r.json()) > 0:
            if "success" in r.json() and not r.json()["success"]:
                event.message.reply(r.json()["message"])
                return

            n = random.randint(0, len(r.json()) - 1)

            embed = MessageEmbed()
            embed.color = cfg.color

            if "large_file_url" in r.json()[n]:
                embed.set_image(url=r.json()[n]["large_file_url"])
            else:
                embed.set_image(url=r.json()[n]["file_url"])

            event.msg.reply('', embed=embed)
