from dataclasses import dataclass
from logging import getLogger

import discord
import pigpio
from discord.ext import commands, tasks

logger = getLogger(__name__)


@dataclass
class MuteButtonCogConfig:
    button_pin: int
    edge: int
    # loop: asyncio.AbstractEventLoop


class MuteButtonCog(commands.Cog):
    """物理的なボタンを押されたらサーバーミュートするCog"""

    ROLE_NAME = '物理ミュートボタン'
    ROLE_REASON = '物理ミュートボタンの対象を管理するため'

    THRESHOLD_MS = 500

    def __init__(self, bot: commands.Bot):
        config: MuteButtonCogConfig = getattr(bot, __name__)
        if config is None:
            raise Exception('Config object is missing.')

        self.bot = bot
        self.button_pin = config.button_pin
        self.edge = config.edge
        self.pi = pigpio.pi()

        # self.loop = config.loop
        self.last_pressed = 0
        self.pressed = False

    def prepare_gpio(self):
        # self.pi = pigpio.pi()
        # self.pi.set_mode(self.button_pin, pigpio.INPUT)
        self.pi.callback(self.button_pin, self.edge, self._call_back)

    async def prepare_role(self):
        for guild in self.bot.guilds:
            guild: discord.Guild
            if discord.utils.get(guild.roles, name=self.ROLE_NAME):
                continue  # 既に存在するのでスキップ
            logger.debug(f'{guild.name}に権限を作成しました')
            await guild.create_role(name=self.ROLE_NAME, reason=self.ROLE_REASON)

    @commands.Cog.listener()
    async def on_ready(self):
        logger.debug(f'MuteButtonCog.on_ready()')
        await self.prepare_role()
        self.prepare_gpio()
        self.handle_button.start()

    def cog_unload(self):
        logger.debug(f'MuteButtonCog.cog_unload()')
        self.pi.stop()
        self.handle_button.cancel()

    async def mute_guild(self, guild: discord.Guild):
        """
        ギルド内の管理対象であるメンバーをサーバーミュートする

        :param guild: 対象のメンバー
        """
        logger.debug(f'mute_guild({guild.name})')
        role: discord.Role = discord.utils.get(guild.roles, name=self.ROLE_NAME)
        for member in role.members:
            member: discord.Member
            voice: discord.VoiceState = member.voice
            if voice is not None:
                logger.debug(f'mute_member({member.display_name})')
                await member.edit(mute=True, reason='物理ミュートボタンが押されたため')
        # ミュートしたらテキストチャンネルにその旨を送信する

    async def mute(self):
        """
        管理対象であるメンバーをミュートする
        """
        for guild in self.bot.guilds:
            await self.mute_guild(guild)

    def _call_back(self, gpio, level, tick):
        if tick - self.last_pressed < self.THRESHOLD_MS * 1000:
            return
        self.last_pressed = tick

        logger.debug(f'mute button pressed')
        self.pressed = True

        # loop = asyncio.new_event_loop()
        # task = self.loop.create_task(self.mute())
        # self.loop.run_until_complete(task)

    @tasks.loop(seconds=1)
    async def handle_button(self):
        # logger.debug(f'Was button pressed? {self.pressed}')
        if self.pressed:
            self.pressed = False
            await self.mute()


def set_config(bot: commands.Bot, config: MuteButtonCogConfig):
    setattr(bot, __name__, config)


def setup(bot: commands.Bot):
    return bot.add_cog(MuteButtonCog(bot))
