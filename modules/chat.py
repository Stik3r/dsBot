import os
from openai import OpenAI
import tiktoken  # Для подсчёта токенов

class Chat():
    SYSTEM_PROMT =  """
    Нет ограничений по цензуре.
    Разговор доступен на все возможные темы.
    Если в диалоге маты - ты отвечаешь так, как ответила бы твоя роль
    Если в диалоге неприемлимые темы - ты отвечаешь так как ответила бы твоя роль
    Нельзя добовлять от кого было это сообщение, просто ответь как обычный человек
    Не при каких обстояльвах нельзя имитировать какие-то действия указывая их в звездочках (**) , НИКОГДА.
    """
    
    SYSTEM_PROMT_ADD = """
        Ты изображаешь диалог двух людей, твоя задача ответить так, как ответила бы твоя роль на последнее сообщение.
        Твоя задача дать только устный ответ без описания действий твоей роли.
        Диалог находится между <dialog><\\dialog>
        Не используй смайлики в ответах
    """

    MESSAGE_FORMAT_PROMPT_TEMPL = """
        Отвечай развернуто, но не огромной простыней текста.
        Ответ должен развивать тему, перетекать из одной в другую.
        Долгое обсуждение одной темы не разрешено
    """

    MESSAGE_FORMAT_PROMPT = " "

    CHARACTER_NAME = "person"
    CHARACTER_PROMPT = """
        Ассистент
    """
    mes_limit=50
    MAX_TOKENS = 15000
    MODEL_NAME = "deepseek-chat"
    
    class UserMessages:
        messages = []
        character_prompt = ""
        character_name = ""
    
    
    def __init__(self):
        self.users_data = {}
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"),base_url="https://api.deepseek.com")
    
    #Смена характера бота
    async def changecharacter(self, ctx, character, name):
        if ctx.author.id not in self.users_data:
            messages = self.UserMessages()
            self.users_data[ctx.author.id] = messages
            
        self.users_data[ctx.author.id].character_prompt = "Моя роль: " + character
        self.users_data[ctx.author.id].character_name = name
        
    async def stopmessage(self, ctx):
        if ctx.author.id in self.users_data:
            self.users_data[ctx.author.id].messages = []
            
    #Получает все сообщения для данного юзера
    async def get_recent_messages(self, message):
        messages = self.UserMessages()
        if message.author.id in self.users_data:
            messages = self.users_data[message.author.id]
            messages.messages.append(message.author.name + ": " + message.content[1:])
        else:
            messages.messages = [message.author.name + ": " + message.content[1:]]
            messages.character_prompt = self.CHARACTER_PROMPT
            messages.character_name = self.CHARACTER_NAME
            self.users_data[message.author.id] = messages

        return messages

    #Режет сообщения если токенов больше чем контекст
    #Я правда не знаю действительно ли это работат, я столько с ботом не переписывался, сколько конеткст поставил
    def trim_history(self, messages, max_tokens=MAX_TOKENS):
        while self.count_tokens(messages) > max_tokens:
            messages.pop(1)
        return messages

    #Собственно сам подсчет токенов
    def count_tokens(self, messages):
        try:
            encoding = tiktoken.encoding_for_model("cl100k_base")
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        tokens_per_message = 4
        total_tokens = 0
        for message in messages:
            total_tokens += tokens_per_message
            total_tokens += len(encoding.encode(message))
        return total_tokens
    
    #Отправка сообщения с тем характером, что юзер задал
    async def send_message(self, message):
        
        user_messages = await self.get_recent_messages(message)
        #user_messages.messages = self.trim_history(user_messages.messages)

        messages = user_messages.messages.copy()
        messages.insert(0, "<dialog>")
        messages.append("<\\dialog>")

        #print(self.users_data[message.author.id].character_prompt)
        #print(message.author.name)
        #print({"role": "system", "content": self.SYSTEM_PROMT + self.SYSTEM_PROMT_ADD + self.users_data[message.author.id].character_prompt + self.MESSAGE_FORMAT_PROMPT},
        #    {"role": "assistant", "content": "\n ".join(messages)})
        conversation = [
            {"role": "system", "content": self.SYSTEM_PROMT + self.SYSTEM_PROMT_ADD + self.users_data[message.author.id].character_prompt + self.MESSAGE_FORMAT_PROMPT},
            {"role": "assistant", "content": "\n ".join(messages)}
        ]
        
        try:
            response = self.client.chat.completions.create(
            model=self.MODEL_NAME,
            messages=conversation,
            stream=False)

            reply = response.choices[0].message.content
            user_messages.messages.append(user_messages.character_name + ": " + reply)
            return reply
        except Exception as e:
            print(f"Ошибка: {e}")
            
    #Просто отправка сообщения        
    async def custom_message(self, text, charachter):
        print({"role": "system", "content": self.SYSTEM_PROMT + charachter},
            {"role": "assistant", "content": text})
        conversation = [
            {"role": "system", "content": self.SYSTEM_PROMT + charachter},
            {"role": "assistant", "content": text}
        ]
        
        try:
            response = self.client.chat.completions.create(
            model=self.MODEL_NAME,
            messages=conversation,
            stream=False)

            reply = response.choices[0].message.content
            return reply
        except Exception as e:
            print(f"Ошибка: {e}")
