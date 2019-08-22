from disco.bot import Plugin
from disco.types.message import MessageEmbed
import config as cfg

class Help(Plugin):
    
    def load(self, ctx):
        super(Help, self).load(ctx)
        self.cmds = {}

        for plugin_name in self.bot.plugins:
            plugin = self.bot.plugins[plugin_name]
            if hasattr(plugin, "category") and hasattr(plugin, "cmds"):
                if plugin.category not in self.cmds:
                    self.cmds[plugin.category] = {}
                
                self.cmds[plugin.category].update(plugin.cmds)

    @Plugin.command('help', parser=True)
    @Plugin.parser.add_argument('category', type=str, default="", nargs='?')
    def on_commands(self, event, args):
        embed = MessageEmbed()
        embed.color = cfg.color

        if len(args.category) > 0:
            for cat in self.cmds:
                if args.category.lower() in cat.lower():
                    embed.title = cat
                    
                    for k in self.cmds[cat]:
                        embed.add_field(name="`{}`".format(self.cmds[cat][k][0]), value=self.cmds[cat][k][1], inline=False)
                    event.msg.reply('', embed=embed)
                    return

            event.msg.reply("Category not found")
            return

        embed.title = "Commands"
        embed.description = "`!help` show this message\n`!help <category>` show more info for category"

        for cat in self.cmds:
            embed.add_field(name=cat, value="`{}`".format(' '.join(x for x in self.cmds[cat])), inline=False)
        event.msg.reply('', embed=embed)
