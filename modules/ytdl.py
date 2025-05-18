import discord
from discord.ext import commands
from discord import Option
import yt_dlp
import asyncio

# Настройки для yt-dlp
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'cookiefile': 'cookies.txt',
    'verbose': True,
}

ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music():
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}

    def check_queue(self, member, guild_id):
        if self.queues.get(guild_id):
            voice = member.guild.voice_client
            source = self.queues[guild_id].pop(0)

            def after_playing(error):
                if error:
                    print(f'Player error: {error}')
                if len(self.queues[guild_id]) > 0:
                    self.check_queue(member, guild_id)
                else:
                    asyncio.run_coroutine_threadsafe(voice.disconnect(), self.bot.loop)

            voice.play(source, after=after_playing)
            voice.source.volume = 0.5

    async def join(self, message):
        if message.author.voice is None:
            return await message.reply("Вы не в голосовом канале!")

        channel = message.author.voice.channel
        voice_client = discord.utils.get(self.bot.voice_clients, guild=message.guild)
        if voice_client is not None:
            await voice_client.move_to(channel)
        else:
            await channel.connect()

        #await message.reply(f"Присоединился к {channel.name}")

    async def leave(self, message):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=message.guild)
        if voice_client is not None:
            await voice_client.disconnect()
        else:
            await message.reply("Я не в голосовом канале!")

    async def play(self, message, url):
        if message.author.voice is None:
             return await message.reply("Вы не в голосовом канале!")

        channel = message.author.voice.channel
        voice_client = discord.utils.get(self.bot.voice_clients, guild=message.guild)
        if voice_client is None:
            await channel.connect()
        elif voice_client.channel != channel:
            await voice_client.move_to(channel)

        voice_client = discord.utils.get(self.bot.voice_clients, guild=message.guild)
        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        
        if message.guild.id not in self.queues:
            self.queues[message.guild.id] = []
        
        if voice_client.is_playing():
            self.queues[message.guild.id].append(player)
            return await message.reply(f"Добавлено в очередь: {player.title}")
        else:
            voice_client.play(player, after=lambda e: self.check_queue(message.author, message.guild.id))
            await message.reply(f"Сейчас играет: {player.title}")

    async def pause(self, message):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=message.guild)
        if voice_client.is_playing():
            voice_client.pause()

    async def resume(self, message):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=message.guild)
        if voice_client.is_paused():
            voice_client.resume()


    async def stop(self, message):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=message.guild)
        if voice_client.is_playing() or voice_client.is_paused():
            voice_client.stop()
            if message.guild.id in self.queues:
                self.queues[message.guild.id] = []

    async def skip(self, message):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=message.guild)
        if voice_client.is_playing():
            voice_client.stop()
            self.check_queue(message.author, message.guild.id)


    async def queue(self, message):
        if message.guild.id in self.queues and len(self.queues[message.guild.id]) > 0:
            queue_list = "\n".join([f"{i+1}. {song.title}" for i, song in enumerate(self.queues[message.guild.id])])
            await message.reply(f"Очередь воспроизведения:\n{queue_list}")
        else:
            await message.reply("Очередь пуста")