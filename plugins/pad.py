from disco.bot import Plugin
from disco.types.message import MessageEmbed
from logging import Handler
from collections import deque
from threading import Timer
from flask import request
import requests, urllib, datetime, logging

from padReader import PadReader, Pad
from pad_monitoring import ChannelClient, PadMonitorSet, PadMonitor
from util.txt2img import Txt2Img, ImageUploadError
import padScraper as ps

from util.pad_functions import get_role_variations, get_all_roles, get_correct_inst, wrap_lines
import config as cfg

import plugins.paginator as paginator

class ErrorHandler(Handler):
    errors = deque([], maxlen=100)

    def emit(self, record):
        log_entry = self.format(record)
        print(log_entry)
        self.errors.appendleft(log_entry)

    def empty(self):
        return len(self.errors) == 0

class PadPlugin(Plugin):

    @Plugin.route('/create', methods=['POST'])
    def flask_monitoring(self):
        if request.method == 'POST' and request.is_json:
            content = request.get_json()
            pad_id = content["pad_id"]
            title = pad_id.replace("_"," ")
            url = "{}?{}".format(cfg.pad_loc, urllib.parse.quote(pad_id))

            self.monitor_set.add(Pad(
                id = pad_id,
                title = title,
                needs = [],
                sheets = {},
                url = url
            ))

            embed = MessageEmbed()
            embed.color = cfg.color

            embed.description = "pad [{}]({}) was created".format(title, url)
            self.channel_client.send_message('', embed=embed)

            return "", 200
        
        return "", 403

    def load(self, ctx):
        super(PadPlugin, self).load(ctx)

        self.category = "Pad"
        self.cmds = {}
        self.cmds["songinfo"] = ["!songinfo <songname>", "Get the pad notes for a song"]
        self.cmds["parts"] = ["!parts <songname>", "List the needed parts for a song"]
        self.cmds["songpart"] = ["!songpart <song_name> <instrument>", "Get PDF link(s) that match the corresponding instrument"]
        self.cmds["needs"] = ["!needs <instrument|@person|me> ", "List all songs that are needed"]

        self.pad_reader = PadReader()
        self.t2i = Txt2Img()

        self.session = requests.Session() # cookies
        #self.session.keep_alive = False
        #self.session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=200, pool_maxsize = 200))

        self.last_refresh = datetime.datetime.now()
        self.time_started = self.last_refresh

        self.channel_client = ChannelClient(self, cfg.ch_oke_a_)

        self.error_handler = ErrorHandler()
        self.error_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", "%Y-%m-%d %H:%M:%S"))

        logging.getLogger(PadMonitor.__name__).addHandler(self.error_handler)

        self.monitor_set = None
        self.restart_monitoring()
        
    def unload(self, ctx):
        super(PadPlugin, self).unload(ctx)
        self.monitor_set.close()

    def restart_monitoring(self):
        if self.monitor_set:
            self.monitor_set.close()
        self.monitor_set = PadMonitorSet(
            self.pad_reader.getpads(),
            self.channel_client,
            self.session,
            self.t2i,
            interval=cfg.pm_interval,
            grace=cfg.pm_grace)
        self.monitor_set.start()

    @Plugin.command('parts', '<content:str...>')
    def on_parts_command(self, event, content):
        pad = self.pad_reader.find_pad(content)

        if not pad:
            event.msg.reply('Dude weed lmao cannot find shit')
            return
            
        embed = MessageEmbed()
        embed.title = pad.title
        embed.url = pad.url
        embed.color = cfg.color
        embed.description = ", ".join(str(x) for x in pad.needs)
        event.msg.reply('', embed=embed)

    @Plugin.command('songinfo', '<content:str...>')
    def on_songinfo(self, event, content):
        pad = self.pad_reader.find_pad(content)
        
        if not pad:
            event.msg.reply('Dude weed lmao cannot find shit')
            return
        
        embed = MessageEmbed()
        embed.title = pad.title
        embed.color = cfg.color
        embed.set_footer(text=pad.id)
        embed.url = pad.url
        if len(pad.needs) > 0:
            embed.add_field(name='needs', value=', '.join(str(x) for x in pad.needs), inline=True)
        embed.set_image(url="https://cdn.discordapp.com/attachments/142137354084155393/437387811663118336/loadingu.gif")
        message = event.msg.reply('', embed=embed)
        
        try:
            text = ps.get_pad_text(self.session, pad.id)
            text = text[:text.find("~~~~~~~~")]
            img = self.t2i.create_img(wrap_lines(text), False)
            embed.set_image(url=img)
            message.edit(embed = embed)
        except ImageUploadError as e:
            logging.getLogger(self).error(e)

    @Plugin.command('songpart', parser=True)
    @Plugin.parser.add_argument('name', type=str)
    @Plugin.parser.add_argument('part', type=str)
    def on_songpart_command(self, event, args):
        part = "\n".join(self.pad_reader.get_sheet(args.name, args.part))
        event.msg.reply(part)

    @Plugin.command('needs', '<content:str...>')
    def on_needed(self, event, content):
        users = []
        
        if len(event.msg.mentions) > 0:
            for a in event.msg.mentions:
                users.append(event.msg.guild.get_member(a))

        elif len(content) == 2 and "me" in content.lower():
            users.append(event.member)

        if len(users) != 0:
            for a in users:
                roles = get_all_roles(a)
                self.print_needs(event, roles, a.user.username + "#" + a.user.discriminator)

        elif len(event.msg.mention_roles) > 0:
            for a in event.msg.mention_roles:
                self.print_needs(event, get_role_variations(event.msg.guild.roles.get(a).name.lower()), event.msg.guild.roles.get(a).name)

        else:
            self.print_needs(event, get_correct_inst(content.replace("_", " ")),  content)
            
    def print_needs(self, event, roles, name):
        songs = self.pad_reader.get_inst_songs(self.pad_reader.getpads(), roles)
        
        if not songs:
            event.msg.reply("Hmm, doesn't seem to be anything...")
        else:
            embed = MessageEmbed()
            embed.title = "In need of " + name
            embed.color = cfg.color
            embed.description = ""
            for k, v in songs:
                embed.description = embed.description + "({}) [{}]({}) `{}`\n".format(str(len(k.needs)), k.title, k.url, ", ".join(v))
                
            paginator.create(self, embed, event.msg.reply)

    @Plugin.command('stopmonitoring')
    def on_stopmonitoring(self, event):
        if cfg.role_codemonkey in event.member.roles or cfg.role_burgmen in event.member.roles:
            self.monitor_set.close()

            event.msg.reply("Stopped monitoring pads")

    @Plugin.command('restartmonitoring')
    def on_startmonitoring(self, event):
        if cfg.role_codemonkey in event.member.roles or cfg.role_burgmen in event.member.roles:
            self.restart_monitoring()
            event.msg.reply("Started monitoring pads")

    @Plugin.command('status')
    def on_status(self, event):
        embed = MessageEmbed()
        embed.title = "DC's Imouto"
        embed.color = cfg.color
        embed.add_field(name='pads monitoring', value=self.monitor_set.num_alive(), inline=True)
        embed.add_field(name='last refresh', value=self.last_refresh.strftime('%Y-%m-%d %H:%M:%S'), inline=True)
        embed.add_field(name='started', value=self.time_started.strftime('%Y-%m-%d %H:%M:%S'), inline=True)
        event.msg.reply('', embed=embed)
