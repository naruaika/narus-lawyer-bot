import discord
import json
import os
import random
import re
from dotenv import load_dotenv
from transformers import pipeline
from transformers import BlenderbotTokenizer
from transformers import BlenderbotForConditionalGeneration

load_dotenv()

client = discord.Client()

sentiment_classifier = pipeline('sentiment-analysis')
tokenizer = BlenderbotTokenizer.from_pretrained('facebook/blenderbot-400M-distill')
converse_model = BlenderbotForConditionalGeneration.from_pretrained('facebook/blenderbot-400M-distill')

tag_finder = re.compile('<.*?>')

with open('words.json', 'r') as f:
    words = json.loads(f.read())
    greeting_words = words['greeting']
    encouraging_words = words['encouraging']
    naugthy_words = words['naugthy']


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    # Do nothing if the message is from the bot itself
    if message.author == client.user:
        return

    # Do nothing if the message is from the other bot
    if message.author.bot:
        return

    response = []

    # Normalise the message
    msg = message.content.lower()

    # Filter the message
    msg_words = msg.split()
    for naughty_word in naugthy_words:
        if any(naughty_word == word for word in msg_words):
            # Sensor the message
            # msg = message.content.replace(naughty_word, len(naughty_word) * '*')
            # await message.edit(content=msg)

            # Warn the user
            await message.channel.send(f"Hey {message.author.mention}, don't talk badly!")
            return

    # Classify the message
    msg_sentiment = sentiment_classifier(msg)

    if msg_sentiment[0]['label'] == 'NEGATIVE' and msg_sentiment[0]['score'] > 0.8:
        # Respond to the depressing message
        encouraging_word = random.choice(encouraging_words)
        encouraging_sentence = encouraging_word.replace('{user}', message.author.mention)
        response.append(encouraging_sentence)

    else:
        # Respond to the greeting message
        if msg.startswith(tuple(greeting_words)):
            greeting_word = random.choice(greeting_words)
            greeting_sentence = f'{greeting_word}, {message.author.mention}!'
            response.append(greeting_sentence)

        # Respond to the message
        msg_token = tokenizer(msg, return_tensors='pt')
        msg_reply = converse_model.generate(**msg_token)
        msg_reply = tokenizer.decode(msg_reply[0])
        msg_reply = re.sub(tag_finder, '', msg_reply)
        response.append(msg_reply)

    # Provide a help
    # if message.channel.name == 'help':
    #     if 'help' in msg:
    #         response.append("I'm here to help you!")

    if response:
        await message.channel.send(' '.join(response))

client.run(os.getenv('TOKEN'))
