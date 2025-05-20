import os
import discord
import whisper
from datetime import datetime 
from discord.ext import commands
from dotenv import load_dotenv
from discord import Option
from modules.ytdl import Music
from modules.chat import Chat

load_dotenv()

intents = discord.Intents.all()
intents.messages = True  # Для работы с сообщениями
intents.message_content = True  # Для чтения текста сообщений (привилегированный!)
intents.members = True  # Для доступа к участникам (привилегированный!)
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)
chat = Chat()
music = Music(bot, chat)

model = whisper.load_model("small")

#Смена персонажа
@bot.slash_command(name="changecharacter", description="Смена характера бота")
async def changecharacter(ctx, arg: Option(str, description="Описание характера", required=True), arg2: Option(str, description="Имя", required=True)):
    await chat.changecharacter(ctx, arg, arg2)
    await ctx.respond("✅ Системный промпт обновлен! \n Теперь моя роль: " + arg)

#Прекращение контекста для пользователя
@bot.slash_command(name="stopmessage", description="Стоп слово для бота")
async def stopmessage(ctx):
    await chat.stopmessage(ctx)
    await ctx.respond("❎ Контекст очищен")

@bot.event
async def on_ready():
    print(f"Бот {bot.user} готов!")

#Обработка сообщений
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("!"):

        if message.content.startswith("!play "):
            result = message.content.replace("!play ", "", 1)
            return await music.play(message, url=result)
        elif message.content.startswith("!join"):
            return await music.join(message)
        elif message.content.startswith("!leave"):
            return await music.leave(message)
        elif message.content.startswith("!pause"):
            return await music.pause(message)
        elif message.content.startswith("!resume"):
            return await music.resume(message)
        elif message.content.startswith("!stop"):
            return await music.stop(message)
        elif message.content.startswith("!skip"):
            return await music.skip(message)
        elif message.content.startswith("!queue"):
            return await music.queue(message)
        elif message.content.startswith("!record"):
            return await start_recording(message)
        elif message.content.startswith("!endrecord"):
            return await stop_recording(message)
        
        
        
        return await chat.send_message(message)  
    
async def start_recording(message):
    await music.join(message)
    voice_client = discord.utils.get(bot.voice_clients, guild=message.guild)
    sink = discord.sinks.MP3Sink()
    
    voice_client.start_recording(
        sink,
        finished_callback,
        message.channel,
    )
        
    await message.reply(f"Начал запись в канале {voice_client.channel.name}!")

async def finished_callback(sink, channel, *args):
    
    for user_id, audio in sink.audio_data.items():
        user = await channel.guild.fetch_member(user_id)
        filename = f"{user.name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp3"
        with open(filename, "wb") as f:
            f.write(audio.file.getbuffer())


        result = model.transcribe(filename, language="ru")
        print(result)
        if len(result['text']) != 0:
            print(len(result["text"]))
        else:
            print("Я лох")
        
        os.remove(filename)
        
        
async def stop_recording(message):
    voice_client = message.guild.voice_client
    if not voice_client or not voice_client.recording:
        await message.reply("Сейчас нет активной записи!")
        return

    voice_client.stop_recording()
    await message.reply("Запись остановлена!")

bot.run(os.getenv("DISCORD_TOKEN"))

