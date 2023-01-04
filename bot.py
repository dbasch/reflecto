import os
import discord
import openai
from dotenv import load_dotenv
from collections import defaultdict
import datetime

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
#see this tutorial if you don't have the above
#https://realpython.com/how-to-make-a-discord-bot-python/

openai.api_key=os.getenv('OPENAI_API_KEY')

queue = defaultdict(list)
start =  datetime.datetime.now().strftime("%H:%M on %A.%B %-d %Y")

def GPT_Completion(texts):
## Call the API key under your account (in a secure way)
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt =  texts,
        temperature = 0.7,
        top_p = 1,
        max_tokens = 256,
        frequency_penalty = 0,
        presence_penalty = 0
    )
    return response.choices[0].text

def textlen(q):
    return sum(map(len, q))

def store(guild, a, m):
    queue[guild].append(a + ": " + m)
    while(textlen(queue[guild]) > 2048):
        queue[guild].pop(0)

async def reply(guild, message, ourname):
    now =  datetime.datetime.now().strftime("%H:%M on %A.%B %-d %Y")
    prompt = "a chatbot named [" + ourname + "] has been listening in a chatroom since " + start + ". It is now " + now + ". The bot's training data ends in late 2021. The bot responds when mentioned like this: @" + ourname + "\n\n"  + "\n".join(queue[guild]) + "\n[" + ourname + "]: "
    print(prompt)
    text = GPT_Completion(prompt)
    store(guild, ourname, text)
    print(text)

    #`t = ".".join(text.split(".")[:-1])
    await message.channel.send(text)


client = discord.Client()
@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    #print("our user is;", client.user.id)
    ourname = client.user.name
    print("our name is:", ourname)
    uid = str(client.user.id)
    author = message.author.name
    mention = message.author.mention
    content = message.content
    guild = message.guild
    mentioned = False
    if content.startswith("<@" + uid):
        print("we were mentioned")
        mentioned = True
        content = content.replace("<@" + uid + ">", "@" + ourname)

    store(guild, author, content)
    if(mentioned):
        await reply(guild, message, ourname)
    print("message count:", len(queue[guild]))
    print("queue:", queue[guild])

client.run(TOKEN)
