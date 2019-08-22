from disco.bot import Plugin
from disco.types.message import MessageEmbed
import config as cfg
from util.txt2img import upload

# create paginators for text and image data
class Paginator(Plugin):

    def load(self, ctx):
        super(Paginator, self).load(ctx)
        self.paginators_as_list = []
        self.paginators = {}

    @Plugin.listen('MessageReactionAdd')
    @Plugin.listen('MessageReactionRemove')
    def on_reaction(self, event):
        if event.message_id in self.paginators and event.user_id != self.state.me.id:
            paginator = self.paginators[event.message_id]
            
            paginator["page"] = paginator["page"] + (1 if event.emoji.name == "➡" else -1)

            if paginator["page"] < 0:
                paginator["page"] = 0

            if "pages" in paginator:
                if paginator["page"] >= len(paginator["pages"]):
                    paginator["page"] = len(paginator["pages"]) - 1

                paginator["embed"].description = paginator["pages"][paginator["page"]]
                paginator["embed"].set_footer(text="{}/{}".format(paginator["page"] + 1, len(paginator["pages"])))
                paginator["message"].edit("", embed=paginator["embed"])

            elif "images" in paginator:
                if paginator["page"] >= len(paginator["images"]):
                    paginator["page"] = len(paginator["images"]) - 1

                change_image(paginator["embed"], paginator["images"][paginator["page"]])
                paginator["embed"].set_footer(text="{}/{}".format(paginator["page"] + 1, len(paginator["images"])))

                paginator["message"].edit("", embed=paginator["embed"])

    def create(self, embed, fn):
        pages = [""]

        for line in embed.description.split("\n"):
            if len(line) <= 0:
                continue
            if len(pages[len(pages) - 1].split("\n")) < 11:
                pages[len(pages) - 1] = pages[len(pages) - 1] + "\n" + line
            else:
                pages.append(line)

        embed.description = pages[0]
    
        if len(pages) > 1:
            embed.set_footer(text="1/{}".format(len(pages)))

        message = fn("", embed=embed)

        if len(pages) > 1:
            self.paginators_as_list.append(message.id)
            self.paginators[message.id] = {"page": 0, "pages": pages, "message": message, "embed": embed}

            message.add_reaction("⬅")
            message.add_reaction("➡")

        if len(self.paginators_as_list) > 100:
            self.paginators.pop(self.paginators_as_list[0], None)
            self.paginators_as_list.pop(0)

    def create_images(self, embed, images, fn):
        change_image(embed, images[0])
    
        if len(images) > 1:
            embed.set_footer(text="1/{}".format(len(images)))

        message = fn("", embed=embed)

        if len(images) > 1:
            self.paginators_as_list.append(message.id)
            self.paginators[message.id] = {"page": 0, "images": images, "message": message, "embed": embed}

            message.add_reaction("⬅")
            message.add_reaction("➡")

        if len(self.paginators_as_list) > 100:
            self.paginators.pop(self.paginators_as_list[0], None)
            self.paginators_as_list.pop(0)

def change_image(embed, image):
    if image["path"] == None:
        image["path"] = upload(image["data"])
        image["data"] = None
    
    embed.set_image(url=image["path"])

def create(plugin, embed, fn):
    plugin.bot.plugins["Paginator"].create(embed, fn)
        
def create_images(plugin, embed, images, fn):
    plugin.bot.plugins["Paginator"].create_images(embed, images, fn)
