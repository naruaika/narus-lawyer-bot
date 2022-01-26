import discord
import json
import os
import random

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
    # Do nothing if the message is from the bot
    if message.author == client.user:
        return

    # Normalise the message
    message_normalised = message.content.lower()

    # Respond to the greeting
    if message_normalised.startswith(tuple(greeting_words)):
        greeting_word = random.choice(greeting_words).capitalize()
        await message.channel.send(f'{greeting_word}, {message.author.name}!')

client.run(os.getenv('TOKEN'))
