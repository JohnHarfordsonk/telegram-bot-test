import random
import requests
import json
import os
import time
import threading
import datetime
import pytz
from gtts import gTTS
from io import BytesIO
from PIL import Image
from urllib.request import urlopen
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Telegram bot token
TOKEN = 'your_token_here'

# Create Updater object and pass in bot token
updater = Updater(TOKEN, use_context=True)

# Define command handlers
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm a bot. Send /help to see what I can do.")

def help(update, context):
    help_text = """Here are the available commands:
/meme - Send a random meme
/joke - Send a random joke
/translate - Translate text between languages
/remindme - Set a reminder for a certain event or task
/play - Play a music or audio file
"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)

def get_random_meme():
    # API endpoint for random memes
    url = 'https://meme-api.herokuapp.com/gimme'

    # Make request to API
    response = requests.get(url)

    # Parse JSON response
    data = json.loads(response.text)

    # Get meme image URL
    image_url = data['url']

    # Open image URL and convert to Image object
    image = Image.open(BytesIO(urlopen(image_url).read()))

    return image

def meme(update, context):
    # Get random meme
    meme_image = get_random_meme()

    # Send meme to user
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=meme_image)

def get_random_joke():
    # API endpoint for random jokes
    url = 'https://official-joke-api.appspot.com/random_joke'

    # Make request to API
    response = requests.get(url)

    # Parse JSON response
    data = json.loads(response.text)

    # Get joke setup and punchline
    setup = data['setup']
    punchline = data['punchline']

    return setup, punchline

def joke(update, context):
    # Get random joke
    setup, punchline = get_random_joke()

    # Send joke setup to user
    context.bot.send_message(chat_id=update.effective_chat.id, text=setup)

    # Wait for 2 seconds
    time.sleep(2)

    # Send joke punchline to user
    context.bot.send_message(chat_id=update.effective_chat.id, text=punchline)

def translate(update, context):
    # Get source language and text to translate from user input
    source_lang, text = context.args

    # Set target language to English
    target_lang = 'en'

    # API endpoint for language translation
    url = f'https://translate.googleapis.com/translate_a/single?client=gtx&sl={source_lang}&tl={target_lang}&dt=t&q={text}'

    # Make request to API
    response = requests.get(url)

    # Parse JSON response
    data = json.loads(response.text)

    # Get translated text
    translated_text = data[0][0][0]

    # Send translated text to user
    context.bot.send_message(chat_id=update.effective_chat.id, text=translated_text)


def set_reminder(bot, update, args):
    # Get the reminder message and time from the command arguments
    reminder_message = ' '.join(args[:-1])
    reminder_time = args[-1]

    # Convert the reminder time to a datetime object
    try:
        reminder_time = datetime.datetime.strptime(reminder_time, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        update.message.reply_text('Invalid datetime format. Use YYYY-MM-DD HH:MM:SS.')
        return

    # Calculate the time difference between the reminder time and now
    time_delta = (reminder_time - datetime.datetime.now()).total_seconds()

    # Check if the reminder time has already passed
    if time_delta < 0:
        update.message.reply_text('Reminder time has already passed.')
        return

    # Define a function to send the reminder message
    def send_reminder():
        bot.send_message(chat_id=update.message.chat_id, text=reminder_message)

    # Start a new thread to send the reminder after the time difference
    threading.Timer(time_delta, send_reminder).start()

    # Confirm the reminder has been set
    update.message.reply_text(f'Reminder set for {reminder_time}.')

# Define a function to handle incoming messages
def handle_message(update, context):
    # Get the message text and chat ID
    message = update.message.text
    chat_id = update.message.chat_id
    
    # Check if the message starts with a command
    if message.startswith('/'):
        # Parse the command
        command = message.split()[0][1:]
        
        # Check if it's the meme command
        if command == 'meme':
            # Send a random meme
            send_meme(chat_id)
        # Check if it's the joke command
        elif command == 'joke':
            # Send a random joke
            send_joke(chat_id)
        # Check if it's the reminder command
        elif command == 'reminder':
            # Parse the reminder text and time
            try:
                reminder_text = message.split('\"')[1]
                reminder_time = message.split('\"')[2].strip()
                
                # Set the reminder
                set_reminder(chat_id, reminder_text, reminder_time)
            except:
                # If there was an error parsing the message, send an error message
                context.bot.send_message(chat_id, text='Invalid reminder command. Usage: /reminder "Reminder text" HH:MM AM/PM')
        # Check if it's the translate command
        elif command == 'translate':
            # Parse the text to translate and the target language
            try:
                text_to_translate = message.split('\"')[1]
                target_language = message.split('\"')[2].strip()
                
                # Translate the text and send it back
                translated_text = translate_text(text_to_translate, target_language)
                context.bot.send_message(chat_id, text=translated_text)
            except:
                # If there was an error parsing the message, send an error message
                context.bot.send_message(chat_id, text='Invalid translate command. Usage: /translate "Text to translate" Target language')
        # Check if it's the play command
        elif command == 'play':
            # Parse the audio file URL
            try:
                audio_url = message.split(' ')[1]
                
                # Play the audio file
                play_audio(chat_id, audio_url)
            except:
                # If there was an error parsing the message, send an error message
                context.bot.send_message(chat_id, text='Invalid play command. Usage: /play Audio file URL')
        # If it's an invalid command, send an error message
        else:
            context.bot.send_message(chat_id, text='Invalid command. Try /meme, /joke, /reminder, /translate or /play.')
def main():
    # Create the Updater and pass in the bot token
    updater = Updater(token=TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the message handler function
    dispatcher.add_handler(MessageHandler(Filters.text, handle_message))

    # Start the bot
    updater.start_polling
