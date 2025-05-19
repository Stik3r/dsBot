import os
import discord
import asyncio
import subprocess
from datetime import datetime 
import numpy as np
from discord.ext import commands
from dotenv import load_dotenv
from discord import Option
from modules.ytdl import Music
from modules.chat import Chat

SAMPLE_RATE = 48000  # Частота дискретизации
SILENCE_THRESHOLD = 0.01  # Порог тишины (0.0 - 1.0)
CHUNK_SIZE = 1024

load_dotenv()

intents = discord.Intents.all()
intents.messages = True  # Для работы с сообщениями
intents.message_content = True  # Для чтения текста сообщений (привилегированный!)
intents.members = True  # Для доступа к участникам (привилегированный!)
intents.voice_states = True

bot = commands.Bot(command_prefix='>', intents=intents)
chat = Chat()
music = Music(bot, chat)




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
    
@bot.event
async def on_voice_state_update(member, before, after):
    # Проверяем, был ли пользователь в канале и начал говорить
    if before.channel is not None and after.channel is not None:
        # Если у пользователя изменился статус "говорит" (микрофон активирован)
        if before.self_stream != after.self_stream or before.self_video != after.self_video:
            pass  # Можно добавить логику
        
        # Если пользователь начал говорить (микрофон включен)
        if not before.self_mute and after.self_mute:  # Если был немой, а стал нет
            print(f"{member.name} начал говорить!")
        
        # Если пользователь замьютился (перестал говорить)
        if before.self_mute and not after.self_mute:
            print(f"{member.name} перестал говорить!")

async def start_recording(message):
    await music.join(message)
    

    # Создаем sink для записи аудио
    voice_client = discord.utils.get(bot.voice_clients, guild=message.guild)
    sink = discord.sinks.MP3Sink()
    voice_client.start_recording(
        sink,
        finished_callback,
        message.channel,
    )

    await message.reply(f"Начал запись в канале {voice_client.channel.name}!")

async def finished_callback(sink, channel, *args):
    await sink.vc.disconnect()
    
    for user_id, audio in sink.audio_data.items():
        user = await channel.guild.fetch_member(user_id)
        filename = f"{user.name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp3"
        with open(filename, "wb") as f:
            f.write(audio.file.read())
        #await channel.send(f"Запись пользователя {user.mention} сохранена как {filename}.")
    
async def stop_recording(message):
    voice_client = message.guild.voice_client
    if not voice_client or not voice_client.recording:
        await message.reply("Сейчас нет активной записи!")
        return

    voice_client.stop_recording()
    await message.reply("Запись остановлена!")


bot.run(os.getenv("DISCORD_TOKEN"))

