from disco.bot import Plugin
from disco.types.message import MessageEmbed
from datetime import datetime
import random
import config as cfg

class Roulette(Plugin):
    def load(self, ctx):
        self.category = "Fun"
        self.cmds = {}
        self.cmds["roulette"] = ["!roulette", "Test your luck"]
        
        super(Roulette, self).load(ctx)

    shots = 6
    killed = {}

    @Plugin.command('roulette')
    def on_roulette(self, event):
        if cfg.role_dead in event.member.roles:
            event.msg.reply("ur already ded")
        else:
            n = random.randint(1, self.shots)
            embed = MessageEmbed()
            embed.title = "({}/{})".format(n, self.shots)
            if n == 1:
                try:
                    event.member.add_role(cfg.role_dead)
                except Exception as e:
                    event.msg.reply("{}: {}".format(type(e).__name__, str(e)))
                    return
                embed.title = embed.title + " f"
                embed.color = 16711680
                self.shots = 6
                self.killed[event.member.user.id] = datetime.now()
            else:
                embed.color = cfg.color
                self.shots = self.shots - 1
                
            event.msg.reply('', embed=embed)

    @Plugin.command('revive')
    def on_revive(self, event):
        if cfg.role_dead in event.member.roles:
            event.msg.reply("ur already ded")
        elif not (len(event.member.roles) == 1 and cfg.role_default in event.member.roles):
            for a in event.msg.mentions:
                member = event.msg.guild.get_member(a)
                if cfg.role_dead not in member.roles or member.user.id not in self.killed:
                    event.msg.reply("{}#{} is not dead".format(member.user.username, event.member.user.discriminator))
                    return
                    
                if (datetime.now() - self.killed[member.user.id]).total_seconds() > cfg.rt_revivetime:
                    try:
                        member.remove_role(cfg.role_dead)
                    except Exception as e:
                        event.msg.reply("{}: {}".format(type(e).__name__, str(e)))
                        return
                        
                    del(self.killed[member.user.id])
                    event.msg.reply("You brought {}#{} back to life".format(member.user.username, member.user.discriminator))
                else:
                    event.msg.reply("You can't revive {}#{} yet".format(member.user.username, member.user.discriminator))
        else:
            event.msg.reply("You are not allowed to revive")
