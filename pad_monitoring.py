from urllib.error import URLError
from http.client import BadStatusLine
from collections import namedtuple
from requests.exceptions import ConnectionError
from urllib3.exceptions import ProtocolError, HTTPError
import difflib
import json
import random
import threading
import time
import logging

from disco.types.message import MessageEmbed

import padScraper as ps
import config as cfg
from util.pad_functions import wrap_lines
from util.txt2img import ImageUploadError

# A Pad references an unique pad. The URL here refers to the url used to
# scrape the given pad for data.

class RetryException(Exception):
    pass
  
class ClosingException(Exception):
    pass

class PadMonitorSet:
    # Accepts a list of Pads to start monitoring, posting updates through the
    # given channel client.
    #
    # Monitor checks the pad for a change every interval seconds. If a change
    # is detected, the bot waits for grace seconds before replying with the
    # changes.
    def __init__(self, pads, client, session, t2i, interval, grace):
        self.monitors = {}
        self.client = client
        self.session = session
        self.t2i = t2i
        self.interval = interval
        self.grace = grace
        
        for pad in pads:
            monitor = PadMonitor(pad, client, session, t2i, interval, grace)
            self.monitors[pad.id] = monitor

    def start(self):
        for monitor in self.monitors.values():
            monitor.start()

    def add(self, pad):
        if not pad.id in self.monitors:
            self.monitors[pad.id] = PadMonitor(pad, self.client, self.session, self.t2i, self.interval, self.grace)
            self.monitors[pad.id].start()
    
    def close(self):
        events = [monitor.closeAsync() for monitor in self.monitors.values()]
        for event in events:
            event.wait()

    def num_alive(self):
        return sum(not monitor.is_dead() for monitor in self.monitors.values())

# Wrap API Client for functionality in a specific channel.
class ChannelClient:
    def __init__(self, bot, channel_id):
        self.bot = bot
        self.channel_id = channel_id

    def send_message(self, *args, **kwargs):
        if self.bot.state.channels.get(self.channel_id):
            self.bot.state.channels.get(self.channel_id).send_message(*args, **kwargs)

class PadMonitor:
    def __init__(self, pad, client, session, t2i, interval, grace=0):
        self.pad = pad
        self.client = client
        self.session = session
        self.t2i = t2i
        self.interval = interval
        self.grace = grace
        
        self.closing = threading.Event()
        self.closed = threading.Event()
        self.pad_text = None
        self.pollthread = threading.Thread(
            target=PadMonitor._run,
            args=[self])

    def getLogger(self):
        return logging.getLogger(self.__class__.__name__)

    def get_diff(self, old_text, new_text):
        return list(difflib.unified_diff(
            wrap_lines(old_text),
            wrap_lines(new_text),
            n=3))

    @staticmethod
    def is_add(line):
        return len(line) > 0 and line[0] == '+' and line[1:].strip()

    # Sends a message for the given changes.
    def _handle_diff(self, diff):
        # Skip empty changes.
        if diff:
            embed = MessageEmbed()
            embed.color = cfg.color

            try:
                img = self.t2i.create_img(diff[2:])
                embed.set_image(url=img)
            except ImageUploadError as e:
                self.getLogger().error("{}:{}".format(e, str(e)))

            embed.description = "[{}]({}) was updated".format(self.pad.title, self.pad.url)
            self.client.send_message('', embed=embed)

    def start(self):
        self.pollthread.start()

    # Returns Threading.event() which is set when the poll ends.
    def closeAsync(self):
        self.closing.set()
        return self.closed

    # Wait for a grace period where nothing changed. Returns final text.
    def _wait_for_unchanged(self, ps, current_text):
        diff = []
        while not self.closing.wait(timeout=self.grace):
            new_text = self._get_pad_text(6, 10, True)
            diff = self.get_diff(current_text, new_text)
            if not diff:
                return new_text
            current_text = new_text
        raise ClosingException

    def _get_pad_text(self, tries, sleep=0, fixed=False):
        sleep_time = random.uniform(0, 1)
        fails = 0
        while not self.closing.wait(timeout=sleep_time):
            if fixed:
                sleep_time = sleep + random.uniform(0, 1.0)
            else:
                sleep_time = cfg.pm_coeff * pow(cfg.pm_base, fails) + random.uniform(0, 1.0)
            try:
                return ps.get_pad_text(self.session, self.pad.id)
            except (HTTPError, BadStatusLine, URLError, ConnectionError, ProtocolError, ConnectionResetError) as e:
                fails += 1
                if fails >= tries:
                    self.getLogger().error(
                        "{}: Failed getting text {} times in a row.".format(e, tries))
                    raise RetryException
                else:
                    self.getLogger().error(
                        "{}: Failed getting text. Trying again in {} seconds.".format(e, int(sleep_time)))
        raise ClosingException

    def _poll_changes(self):
        # Add delay to stagger requests.
        time.sleep(random.uniform(0, self.interval))

        # Priming
        try:
            self.pad_text = self._get_pad_text(cfg.pm_maxfails)
        except RetryException:
            self.getLogger().error(
                "Failed getting pad text on startup. Not watching pad {}.".format(self.pad.id))
        except ClosingException:
            return

        sleep_time = self.interval + random.uniform(0, 1)

        # Begin polling.
        while not self.closing.wait(timeout=sleep_time):
            # Jitter to stagger requests more.
            sleep_time = self.interval + random.uniform(0, 1)
            # Check for changes.
            try:
                new_text = self._get_pad_text(cfg.pm_maxfails)
            except ClosingException:
                return

            diff = self.get_diff(self.pad_text, new_text)
            # Wait until a grace period without any changes.
            if diff and self.grace != 0:
                try:
                    new_text = self._wait_for_unchanged(ps, new_text)
                except ClosingException:
                    return
                except RetryException:
                    self.getLogger().error(
                        "Failed waiting for changes")
                diff = self.get_diff(self.pad_text, new_text)

            # Update text.
            self.pad_text = new_text
            self._handle_diff(diff)
        
    def _run(self):
        try:
            self._poll_changes()
        except (RetryException, Exception) as e:
            self.getLogger().error(
                "{}: Not watching pad {}.\n{}".format(type(e).__name__, self.pad.id, str(e)))
        finally:
            self.closed.set()
    
    def is_dead(self):
        return self.closed.is_set()
