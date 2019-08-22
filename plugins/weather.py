from disco.bot import Plugin
from disco.types.message import MessageEmbed
import requests
import config as cfg

class Weather(Plugin):

    def load(self, ctx):
        super(Weather, self).load(ctx)
        self.category = "Searches"
        self.cmds = {}
        self.cmds["weather"] = ["!weather <city>", "Get weather information for city"]

    @Plugin.command('weather', '<content:str...>')
    def on_weather(self, event, content):

        r = requests.get("http://api.openweathermap.org/data/2.5/weather",
            params = {"q" : content, 
            "appid" : cfg.weather_key, 
            "units" : "metric"}).json()

        if r["cod"] == 401:
            event.msg.reply("nothing found")
            return
            
        name = r["name"]
        country = r["sys"]["country"]
        id = r["id"]
        humidity = r["main"]["humidity"]
        temp = r["main"]["temp"]
        temp_min = r["main"]["temp_min"]
        temp_max = r["main"]["temp_max"]
        weather = r["weather"][0]["main"]
        sunrise = r["sys"]["sunrise"]
        sunset = r["sys"]["sunset"]

        embed = MessageEmbed()
        embed.color = cfg.color
        embed.add_field(name=":earth_americas: Location", value="[{}, {}](https://openweathermap.org/city/{})".format(name, country, id), inline=True)
        embed.add_field(name=":sweat: Humidity", value="{}%".format(humidity), inline=True)
        embed.add_field(name=":cloud: Weather", value=weather, inline=True)
        embed.add_field(name=":thermometer: Temperature", value="{:.1f}°C / {:.1f}°F".format(temp, (temp * 9/5) + 32), inline=True)
        embed.add_field(name=":sunny: Min / Max", value="{:.1f}°C - {:.1f}°C\n{:.1f}°F - {:.1f}°F".format(
            temp_min, temp_max, 
            (temp_min * 9/5) + 32, 
            (temp_max * 9/5) + 32), inline=True)
        embed.add_field(name=":sunrise_over_mountains: Sunrise / Sunset", value="{:02.0f}:{:02.0f} UTC / {:02.0f}:{:02.0f} UTC".format(
            (sunrise / (60 * 60)) % 24, 
            (sunrise / 60) % 60, 
            (sunset / (60 * 60)) % 24, 
            (sunset / 60) % 60), inline=True)
            
        event.msg.reply('', embed=embed)
