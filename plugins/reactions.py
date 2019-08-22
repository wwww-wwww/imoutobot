from disco.bot import Plugin
from disco.types.message import MessageEmbed
import config as cfg
import plugins.paginator as paginator
from util.storage import Storage
import re

class Reactions(Plugin):
    def load(self, ctx):
        super(Reactions, self).load(ctx)
        self.reactions = Storage("reactions.json")
        self.category = "Util."
        self.cmds = {}
        self.cmds["acr"] = ["!acr <match> <reply> !acr <match> <reply> <regex:1|0>", "(Admin) Add custom reaction"]
        self.cmds["lcr"] = ["!lcr", "List custom reactions"]
        self.cmds["rcr"] = ["!rcr <id>", "(Admin) Remove custom reaction"]
        
    @Plugin.command('acr', parser=True)
    @Plugin.parser.add_argument('find', type=str)
    @Plugin.parser.add_argument('reply', type=str)
    @Plugin.parser.add_argument('regex', type=int, default=0, nargs='?')
    def on_addcr(self, event, args):
        if not cfg.role_burgmen in event.member.roles and not cfg.role_codemonkey in event.member.roles:
            return

        if not args.regex:
            args.find = "^{}$".format(re.escape(args.find))

        reaction = {
            "find": args.find,
            "reply": args.reply
        }
        self.reactions.append(reaction)

    @Plugin.command('lcr')
    def on_listcr(self, event):
        n = 0

        embed = MessageEmbed()
        embed.color = cfg.color
        embed.description = ""

        for reaction in self.reactions:
            if len(embed.description + "{}. {}\n".format(n, reaction["find"])) > 2048:
                event.msg.reply('', embed=embed)
                embed.description = ""
            embed.description = embed.description + "{}. {}\n".format(n, reaction["find"])
            n = n + 1

        if len(embed.description) > 0:
            paginator.create(self, embed, event.msg.reply)

    @Plugin.command('rcr', parser=True)
    @Plugin.parser.add_argument('index', type=int)
    def on_removecr(self, event, args):
        if not cfg.role_burgmen in event.member.roles and not cfg.role_codemonkey in event.member.roles:
            return

        if args.index >= self.reactions.length():
            event.msg.reply("can't do that")
            return

        find = self.reactions[args.index]["find"]

        if self.reactions.remove(args.index):
            event.msg.reply("removed {}".format(find))
        else:
            event.msg.reply("can't do that")

    @Plugin.listen('MessageCreate')
    def on_message(self, event):
        if event.message.author.bot:
            return
        for reaction in self.reactions:
            if re.search(reaction["find"], event.message.content.lower()):
                event.message.reply(reaction["reply"].replace("%u", event.message.member.mention))
            
