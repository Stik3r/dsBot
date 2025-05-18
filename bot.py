import os
import discord
from discord.ext import commands
from openai import OpenAI
from dotenv import load_dotenv
import tiktoken  # Для подсчёта токенов
from discord import Option
from modules.ytdl import Music
from modules.chat import Chat


load_dotenv()

intents = discord.Intents.default()
intents.messages = True  # Для работы с сообщениями
intents.message_content = True  # Для чтения текста сообщений (привилегированный!)
intents.members = True  # Для доступа к участникам (привилегированный!)

bot = commands.Bot(command_prefix='>', intents=intents)
music = Music(bot)
chat = Chat()



#Смена персонажа
@bot.slash_command(name="changecharacter", description="Смена характера бота")
async def changecharacter(ctx, arg: Option(str, description="Описание характера", required=True), arg2: Option(str, description="Имя", required=True)):
    global CHARACTER_PROMPT
    global CHARACTER_NAME
    global users_data
    users_data[ctx.author.name].character_prompt = "Моя роль: " + arg
    users_data[ctx.author.name].character_name = arg2
    await ctx.respond("✅ Системный промпт обновлен! \n Теперь моя роль: " + arg)

#Прекращение контекста для пользователя
@bot.slash_command(name="stopmessage", description="Стоп слово для бота")
async def stopmessage(ctx):
    global users_data
    if ctx.author.name in users_data:
        users_data[ctx.author.name].messages = []
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
        
        
        
        return await chat.send_message(message)    




bot.run(os.getenv("DISCORD_TOKEN"))
