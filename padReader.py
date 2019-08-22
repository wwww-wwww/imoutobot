from collections import namedtuple
import json, urllib
import padScraper as ps
import config as cfg

Pad = namedtuple('pad', ['id', 'title', 'needs', 'sheets', 'url'])

class PadReader():
    
    # Returns a list of all pads
    def getpads(self):
        pads = []

        for pad_id, v in ps.get_songlist().items():
            if pad_id in cfg.ignored_pads:
                continue

            sheets = ps.get_sheets()

            pads.append(Pad(
                id = pad_id,
                title = pad_id.replace("_", " "),
                needs = v["needs"],
                sheets = None if not sheets[pad_id] else sheets[pad_id],
                url = "{}?{}".format(cfg.pad_loc, urllib.parse.quote(pad_id))
            ))

        return sorted(pads, key=lambda v: len(v.needs))

    def find_pad(self, pad_name):
        for pad in self.getpads():
            if pad_name.lower() in pad.title.lower():
                return pad
        return None

    # Get all songs that need an instruments in list insts
    def get_inst_songs(self, pads, insts):
        songs = []
        for pad in self.getpads():
            needs = []
            for inst in pad.needs:
                if any(item.lower() in inst.lower() for item in insts): 
                    needs.append(inst.lower())
            if needs:
                songs.append((pad, needs))

        return songs
        
    # Get sheets for the instrument
    def get_sheet(self, pad_name, inst_search):
        pad = self.find_pad(pad_name)
        
        if not pad:
            return ["pad not found"]

        insts = []

        for inst, content in pad.sheets.items():
            if inst_search.lower() in inst.lower():
                insts.append("{}: {}".format(inst, content))

        if not insts:
            insts.append("sheets not found")

        return insts
        