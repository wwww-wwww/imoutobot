from disco.bot import Plugin
from disco.types.message import MessageEmbed
import config as cfg

from time import sleep

thinks = [
    ":tinking:587473627134427147",
    ":thurrrrrk:593107657452158977",
    ":thunk:341051314404589568",
    ":thrink:341051278597816322",
    ":thoooooooonk:373210277866373130",
    ":thoink:593108386288107522",
    ":thnkng:341883240010874881",
    ":thinkyikes:593108386292170768",
    ":thinkgun:593108387085156372",
    ":thinkemono:380440725940207616",
    ":thinkeggplant:341051068769239050",
    ":thinkaho:587474643636715560",
    ":thenk:349311010584395788",
    ":theenk:588459547585282050",
    ":thbnk:341051191737712640",
    ":tenk:593109807808905226",
    ":owo:361591703754506242",
    "🤔"
]
    
wdhmbt = ["🇼", "🇩", "🇭", "🇲", "🇧", "🇹"]

bruh = ["🇧", "🇷", "🇺", "🇭"]

class Extra(Plugin):
    def load(self, ctx):
        self.category = "Util."
        self.cmds = {}
        self.cmds["who"] = ["!who <rolename>", "List members who have the role name"]
        
        super(Extra, self).load(ctx)

    @Plugin.command('who', '<content:str...>')
    def on_who(self, event, content):
        tab = event.msg.guild.members
        str = ""
        for user in tab:
            member = event.msg.guild.get_member(user)
            if len([1 for v in member.roles if content.lower() in member.guild.roles.get(v).name.lower()]) > 0:
                str = str + ("{}#{}\n".format(member.user.username, member.user.discriminator))
        
        if len(str) > 0:
            embed = MessageEmbed()
            embed.title = content
            embed.color = cfg.color
            embed.add_field(name='who', value=str, inline=False)
            event.msg.reply('', embed=embed)
            
    @Plugin.command('wdhmbt', '<id:int...>')
    def on_wdhmbt(self, event, id):
        channel = event.msg.guild.channels[event.msg.channel_id]
        message = channel.get_message(id[0])
        for letter in wdhmbt:
            sleep(0.5)
            message.add_reaction(letter)

    @Plugin.command('think', '<id:int...>')
    def on_think(self, event, id):
        channel = event.msg.guild.channels[event.msg.channel_id]
        message = channel.get_message(id[0])
        for think in thinks:
            sleep(0.5)
            message.add_reaction(think)

    @Plugin.command('bruh', '<id:int...>')
    def on_bruh(self, event, id):
        channel = event.msg.guild.channels[event.msg.channel_id]
        message = channel.get_message(id[0])
        for letter in bruh:
            sleep(0.5)
            message.add_reaction(letter)
            