import asyncio
import discord
import json
import os
import random
import re
from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashContext
from discord_slash import SlashCommand
from transformers import BlenderbotTokenizer
from transformers import BlenderbotForConditionalGeneration

load_dotenv()

client = commands.Bot(command_prefix='/')
slash = SlashCommand(client, sync_commands=True)  # TODO: migrate to newly discord built-in

# TODO: add basic knowledge about me
tokenizer = BlenderbotTokenizer.from_pretrained('facebook/blenderbot-400M-distill')
converse_model = BlenderbotForConditionalGeneration.from_pretrained('facebook/blenderbot-400M-distill')

tag_finder = re.compile('\s*<.*?>\s*')
word_finder = re.compile('[^a-zA-Z\s]*')
duplicate_finder = re.compile(r"(.)\1{2,}", re.DOTALL)

with open('words.json', 'r') as f:
    words = json.loads(f.read())


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@slash.slash(name='ping', description='PING!')
async def ping(context):
    await context.send('pong')


@slash.slash(name='me', description='Send a message to Naru.')
async def naru(context: SlashContext, message='Hello, Naru!'):
    print(f'{context.author} says {message} to Naru')

    if message == 'Hello, Naru!':
        await context.send('You just say hello to Naru!')
    else:
        await context.send(f'Your message has been sent to Naru.')

    # TODO: send the message to me in DM


@client.event
async def on_message(message):
    # Execute slash commands
    if message.content.startswith('/'):
        return await client.process_commands(message)

    # Do nothing if the message is from the bot itself
    if message.author == client.user:
        return

    # Do nothing if the message is from a bot
    if message.author.bot:
        return

    # Simulate thinking delay
    await asyncio.sleep(30)

    response = []

    # Pre-process the message
    msg = message.content.lower()  # lowercase
    msg = re.sub(word_finder, '', msg)  # remove non-alphanumeric characters
    msg = duplicate_finder.sub(r"\1\1", msg)  # remove more than 2 duplicate letters

    # Ask the user to speak up
    if (msg.isspace() or msg == ''):
        response.append(f"{message.author.mention}, what weighs on your mind?")
        response.append(f"We can talk in DM if you want.")
        return await message.channel.send(' '.join(response))

    # Log the user message
    if message.channel.type is not discord.ChannelType.private:
        print(f'{message.author} says {msg}')

    # Warn the user if the message contains naughty words
    msg_words = msg.split()
    for naughty_word in words['naugthy']:
        if any(naughty_word == word for word in msg_words):
            response.append(f"Hey {message.author.mention}, don't talk badly!")
            response.append(f"Naru taught me to say nice things only.")
            return await message.channel.send(' '.join(response))

    # Indicate the bot is typing
    async with message.channel.typing():

        # Respond to the greeting message
        if msg in [word.lower() for word in words['greeting']]:
            greeting_word = random.choice(words['greeting'])
            greeting_sentence = f'{greeting_word}, {message.author.mention}!'
            response.append(greeting_sentence)

        # Respond to the message
        msg_token = tokenizer(msg, return_tensors='pt')
        msg_reply = converse_model.generate(**msg_token)
        msg_reply = tokenizer.decode(msg_reply[0])
        msg_reply = re.sub(tag_finder, '', msg_reply)
        response.append(msg_reply)

        if response:
            # Send the response
            await message.channel.send(' '.join(response))

            # Log the bot response
            if message.channel.type is not discord.ChannelType.private:
                print(f"Bot replies {' '.join(response)}")


# Run the bot
client.run(os.getenv('TOKEN'))
