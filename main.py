import discord
import dotenv
import json
import os
import random
import re
import requests

dotenv.load_dotenv()

client = discord.Client()

greeting_words = []


@client.event
async def on_ready():
    global greeting_words
    with open('words.json', 'r') as f:
        words = json.loads(f.read())
        greeting_words = words['greeting']


@client.event
async def on_message(message):
    # Do nothing if the message is from the bot itself
    if message.author == client.user:
        return

    # Do nothing if the message is from the other bot
    if message.author.bot:
        return

    # Normalise the message
    msg = message.content.lower()

    response = []

    # Respond to the greeting
    if msg.startswith(tuple(greeting_words)):
        greeting_word = random.choice(greeting_words).capitalize()
        response.append(f'{greeting_word}, {message.author.mention}!')

    # Provide a help
    # if message.channel.name == 'help':
    #     if 'help' in msg:
    #         response.append("I'm here to help you!")

    await message.channel.send(' '.join(response))

client.run(os.getenv('TOKEN'))
