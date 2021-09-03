import pigpio
from discord.ext import commands
import mute_button_cog

bot = commands.Bot(command_prefix='!')
config = mute_button_cog.MuteButtonCogConfig(button_pin=27, edge=pigpio.EITHER_EDGE)
mute_button_cog.set_config(bot, config)  # <1>
bot.load_extension('icon_cog')  # <2>
bot.run('<bot token>')  # <3>
