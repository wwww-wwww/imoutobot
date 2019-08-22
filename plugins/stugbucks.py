from disco.bot import Plugin
from disco.types.message import MessageEmbed
import config as cfg
from util.storage import Storage

class StugBucks(Plugin):
    def load(self, ctx):
        super(StugBucks, self).load(ctx)

        self.category = "Misc."
        self.cmds = {}
        self.cmds["sbcount"] = ["!sbcount <@user>", "Get user's wallet"]
        self.cmds["sbgive"] = ["!sbgive <@user> <count>", "Give user StuGBucks"]
        self.cmds["sbtop"] = ["!sbtop", "List top wallets"]
        self.bucks = Storage("stugbucks.json")
    
    @Plugin.command("sbcount")
    def on_sbcount(self, event):
        for a in event.msg.mentions:
            event.msg.reply(event.msg.guild.get_member(a).mention + " has " + str(self.get_bucks(a)) + " StuGBucks.")
    
    @Plugin.command('sbgive', '<content:str...>')
    def on_sbgive(self, event, content):
        if len(content.split(" ")) != 2:
            event.msg.reply("Usage: !sbgive @user 10")
            return

        try:
            n = int(content.split(" ")[1])
        except ValueError:
            event.msg.reply("Usage: !sbgive @user 10")
            return

        if n < 0:
            event.msg.reply("Can't give negative StuGBucks.")
        elif n <= self.get_bucks(event.msg.author.id):
            if len(event.msg.mentions) == 1:
                for a in event.msg.mentions:
                    pred = self.bucks[a] + n
                    self.give_bucks(a, n)
                    if self.bucks[a] != pred:
                        event.msg.reply("write error")
                        return
                    self.give_bucks(event.msg.author.id, -n)
                    event.msg.reply("{} gave {} {} StuGBucks.".format(event.msg.member.mention, event.msg.guild.get_member(a).mention, n))
            else:
                event.msg.reply("Usage: !sbgive @user 10")
                return
        else:
            event.msg.reply("You don't have enough StuGBucks.")

    @Plugin.command('sbgrant', '<content:str...>')
    def on_sbgrant(self, event, content):
        n = int(content.split(" ")[1])
        if cfg.role_codemonkey in event.member.roles:
            if len(event.msg.mentions) == 1:
                for a in event.msg.mentions:
                    self.give_bucks(a, n)

    @Plugin.command('sbtop')
    def on_sbtop(self, event):
        tab = []
        for id in self.bucks.keys():
            if str(id) != "210100150566125568":
                person = [id, self.bucks[id]]
                tab.append(person)

        tab = sorted(tab, key=lambda v: v[1], reverse=True)

        s = ""

        n = 0
        while n < min(len(tab),10):
            if event.msg.guild.get_member(tab[n][0]):
                s = s + "{}. {}: {}\n".format(n + 1, event.msg.guild.get_member(tab[n][0]).name, tab[n][1])
                n = n + 1
            
        embed = MessageEmbed()
        embed.title = "StuGBucks Ranking"
        embed.color = cfg.color
        embed.description = s
        event.msg.reply('', embed=embed)

    def get_bucks(self, id):
        if str(id) == "210100150566125568":
            return 999999999
        if str(id) in self.bucks.keys():
            return self.bucks[str(id)]
        return 0
    
    def set_bucks(self, id, n):
        self.bucks[str(id)] = n

    def give_bucks(self, id, n):
        if str(id) != "210100150566125568":
            self.set_bucks(id, self.get_bucks(id) + n)
            