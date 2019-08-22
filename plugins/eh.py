from disco.bot import Plugin
from disco.types.message import MessageEmbed, MessageEmbedThumbnail
import config as cfg
import re, requests
from io import BytesIO

LOGIN_URL = "https://forums.e-hentai.org/index.php?act=Login&CODE=01"
api_ex = "https://exhentai.org/api.php"

# embed e-hentai / ex-hentai links
class EH(Plugin):

    def load(self, ctx):
        super(EH, self).load(ctx)

        self.session = requests.Session()

        self.session.post(LOGIN_URL, data={"UserName": cfg.ehentai_username, "PassWord": cfg.ehentai_password, "CookieDate": "1"})

        self.session.cookies.set("logged_in", "true")
        self.session.cookies.set("login_sessionid", self.session.cookies["ipb_session_id"])
        self.session.cookies.set("login_memberid", self.session.cookies["ipb_member_id"])
        self.session.cookies.set("login_passhash", self.session.cookies["ipb_pass_hash"])

        self.session.get("https://exhentai.org")

    @Plugin.listen('MessageCreate')
    def on_message(self, event):
        if event.member.user.bot:
            return

        m = re.search(r"https{0,1}:\/\/e[x-]hentai.org\/g\/([A-z0-9]+)\/([A-z0-9]+)\/", event.message.content)

        if m and len(m.groups()) == 2:
            r = self.session.post(api_ex, json={
                "method": "gdata",
                "gidlist": [
                    [m.group(1), m.group(2)]
                ],
                "namespace": 1})

            j = r.json()

            embed = MessageEmbed()
            embed.color = cfg.color
            embed.title = j["gmetadata"][0]["title"]
            embed.add_field(name='Tags', value=" ".join(j["gmetadata"][0]["tags"]), inline=True)
            embed.add_field(name='Links', value=("[e-hentai](https://e-hentai.org/g/{0}/{1}/) [exhentai](https://exhentai.org/g/{0}/{1}/)").format(m.group(1), m.group(2)), inline=True)
            embed.add_field(name='test', value="yes" if j["gmetadata"][0]["expunged"] else "no", inline=True)

            imgdata = self.session.get(j["gmetadata"][0]["thumb"].replace("\\", ""))

            resp = requests.post(
                "https://f.okea.moe/api/upload",
                files={'file' : ('1.jpg', BytesIO(imgdata.content))})

            resp_json = resp.json()

            if resp.ok and resp_json and resp_json["success"] == True and resp_json["url"] != None:
                embed.thumbnail = MessageEmbedThumbnail()
                embed.thumbnail.url = resp_json["url"]

            event.reply("", embed=embed)
