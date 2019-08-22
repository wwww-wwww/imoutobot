from disco.bot import Plugin
from disco.types.message import MessageEmbed, MessageEmbedThumbnail
import config as cfg
import re, amiami

# embed amiami links
class Amiami(Plugin):

    @Plugin.listen('MessageCreate')
    def on_message(self, event):
        if not event.member.user.bot:
            m = re.search(r"https*:\/\/w*\.*amiami\.[a-zA-Z]+\/[a-zA-Z\/]+\?gcode=([^\&]+)", event.message.content)
            if m:
                results = amiami.search(m.group(1))
                if len(results.items) > 0:
                    item = results.items[0]

                    embed = MessageEmbed()
                    embed.color = cfg.color
                    embed.title = item.productName
                    embed.url = item.productURL
                    embed.set_footer(text=f"{item.price:,} JPY")

                    embed.thumbnail = MessageEmbedThumbnail()
                    embed.thumbnail.url = item.imageURL

                    event.reply("", embed=embed)
