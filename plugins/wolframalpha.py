from disco.bot import Plugin
from disco.types.message import MessageEmbed, MessageEmbedImage
import config as cfg
import wolframalpha

class WolframAlpha(Plugin):

    def load(self, ctx):
        super(WolframAlpha, self).load(ctx)
        self.wolfram = wolframalpha.Client(cfg.wolfram_key)
        self.category = "Searches"
        self.cmds = {}
        self.cmds["wa"] = ["!wa <query>", "Ask Wolfram Alpha"]

    @Plugin.command('wa', '<query:str...>')
    def on_generate(self, event, query):
        res = self.wolfram.query(query)
        if res.success.lower() == "true":
            results = list(res.results)
            pods = list(res.pods)

            if results:
                answer = results[0]
                if answer.title == "Distribution of total" and "@scanner" in answer and answer.scanner == "Dice":
                    for pod in pods:
                        if pod.title == "Example":
                            answer = pod
                            break
            elif len(pods) > 1:
                answer = pods[1]
            else:
                event.msg.reply("no results")
                return

            if "@scanner" in answer and answer.scanner == "Dice":
                embed = MessageEmbed()
                embed.color = cfg.color
                embed.description = answer.text
                embed.set_image(url=answer["subpod"]["img"]["@src"])
                event.msg.reply("", embed=embed)
            elif answer.text:
                event.msg.reply(answer.text)
            else:
                embed = MessageEmbed()
                embed.color = cfg.color
                embed.set_image(url=answer["subpod"]["img"]["@src"])
                event.msg.reply("", embed=embed)
            
        else:
            event.msg.reply("no results")
            
