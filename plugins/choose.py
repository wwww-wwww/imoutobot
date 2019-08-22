from disco.bot import Plugin
import random

class Choose(Plugin):
    def load(self, ctx):
        self.category = "Fun"
        self.cmds = {}
        self.cmds["choose"] = ["!choose <a>;<b>;<c>", "Have the bot choose for you"]
        
        super(Choose, self).load(ctx)
        
    @Plugin.command('choose', '<content:str...>')
    def on_choose(self, event, content):
        choices = content.split(";")
        choices_lower = content.lower().split(";")

        if "bruh" in choices_lower and "obama gaming" in choices_lower:
            event.msg.reply("obama bruh")
            return

        for choice in choices:
            if choice.lower() == "bruh":
                event.msg.reply(choice)
                return

        if len(choices) > 1:
            event.msg.reply(choices[random.randint(0, len(choices) - 1)])
        else:
            event.msg.reply("not enough choices")
