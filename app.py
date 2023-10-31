# libraries
import requests
import json
import telebot
from telebot import types

# local imports
import config

word_limit = 10
parasite_cur_offset = 0
mispronounced_cur_offset = 0
last_audio_id = None
filter = None

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        chat_id=message.chat.id,
        text=f"Hello, {message.from_user.first_name}!",
    )


@bot.message_handler(commands=["parasite_words"])
def list_parasite_words(message):
    filter = message.text.split()[1:]  # storing user args passed with the command
    filter = " ".join(filter)
    parasite_cur_offset = 0

    if len(filter) == 0:
        parasite_markup = parasite_words_markup(message, parasite_cur_offset)
    else:
        parasite_markup = filter_parasite_words(message, parasite_cur_offset, filter)
    if parasite_markup != None:
        bot.send_message(
            chat_id=message.chat.id,
            text="List of words:",
            reply_markup=parasite_markup,
        )


def parasite_words_markup(message, offset):
    parasite_words = requests.get(
        f"http://duryssoile.nu.edu.kz/api/v1.0/words?type=parasite&offset={offset}&limit={word_limit}&sort=asc"
    )

    if parasite_words.status_code != 200:
        bot.send_message(
            message.chat.id,
            f"Error! {parasite_words.status_code} Status Code recieved",
        )
        return None

    data = json.loads(parasite_words.text)
    markup = types.InlineKeyboardMarkup(row_width=2)

    for word in data:
        btn = types.InlineKeyboardButton(word["word"], callback_data=str(word["id"]))
        markup.add(btn)

    if offset != 0:
        prev_btn = types.InlineKeyboardButton(
            "⏪ Previous", callback_data="parasite_prev_page"
        )
    if len(data) == word_limit:
        next_btn = types.InlineKeyboardButton(
            "Next ⏩", callback_data="parasite_next_page"
        )
    if "prev_btn" in locals():
        markup.row(prev_btn, next_btn)
    elif "next_btn" in locals():
        markup.row(next_btn)

    return markup


def filter_parasite_words(message, offset, filter):
    parasite_words = requests.get(
        f"http://duryssoile.nu.edu.kz/api/v1.0/words?type=parasite&filter={filter}&offset={offset}&limit={word_limit}&sort=asc"
    )

    if parasite_words.status_code != 200:
        bot.send_message(
            message.chat.id,
            f"Error! {parasite_words.status_code} Status Code recieved",
        )
        return None

    data = json.loads(parasite_words.text)

    if len(data) == 0:
        bot.send_message(
            message.chat.id,
            f"No such word exists",
        )
        return None

    markup = types.InlineKeyboardMarkup(row_width=2)

    for word in data:
        btn = types.InlineKeyboardButton(word["word"], callback_data=str(word["id"]))
        markup.add(btn)

    if offset != 0:
        prev_btn = types.InlineKeyboardButton(
            "⏪ Previous", callback_data="parasite_prev_page"
        )
    if len(data) == word_limit:
        next_btn = types.InlineKeyboardButton(
            "Next ⏩", callback_data="parasite_next_page"
        )
    if "prev_btn" in locals():
        markup.row(prev_btn, next_btn)
    elif "next_btn" in locals():
        markup.row(next_btn)

    return markup


@bot.message_handler(commands=["mispronounced_words"])
def list_mispronounced_words(message):
    filter = message.text.split()[1:]  # storing user args passed with the command
    filter = " ".join(filter)
    mispronounced_cur_offset = 0

    if len(filter) == 0:
        markup = mispronounced_words_markup(message, mispronounced_cur_offset)
    else:
        markup = filter_mispronounced_words(message, mispronounced_cur_offset, filter)
    if markup != None:
        bot.send_message(
            chat_id=message.chat.id,
            text="List of words:",
            reply_markup=markup,
        )


def mispronounced_words_markup(message, offset):
    misspronounced_words = requests.get(
        f"http://duryssoile.nu.edu.kz/api/v1.0/words?type=commonly-mispronounced&offset={offset}&limit={word_limit}&sort=asc"
    )
    if misspronounced_words.status_code != 200:
        bot.send_message(
            message.chat.id,
            f"Error! {misspronounced_words.status_code} Status Code recieved",
        )
        return

    data = json.loads(misspronounced_words.text)
    markup = types.InlineKeyboardMarkup(row_width=2)

    for word in data:
        btn = types.InlineKeyboardButton(word["word"], callback_data=str(word["id"]))
        markup.add(btn)

    if offset != 0:
        prev_btn = types.InlineKeyboardButton(
            "⏪ Previous", callback_data="mispro_prev_page"
        )
    if len(data) == word_limit:
        next_btn = types.InlineKeyboardButton(
            "Next ⏩", callback_data="mispro_next_page"
        )
    if "prev_btn" in locals():
        markup.row(prev_btn, next_btn)
    elif "next_btn" in locals():
        markup.row(next_btn)

    return markup


def filter_mispronounced_words(message, offset, filter):
    misspronounced_words = requests.get(
        f"http://duryssoile.nu.edu.kz/api/v1.0/words?type=commonly-mispronounced&filter={filter}&offset={offset}&limit={word_limit}&sort=asc"
    )
    if misspronounced_words.status_code != 200:
        bot.send_message(
            message.chat.id,
            f"Error! {misspronounced_words.status_code} Status Code recieved",
        )
        return

    data = json.loads(misspronounced_words.text)
    if len(data) == 0:
        bot.send_message(
            message.chat.id,
            f"No such word exists",
        )
        return None

    markup = types.InlineKeyboardMarkup(row_width=2)

    for word in data:
        btn = types.InlineKeyboardButton(word["word"], callback_data=str(word["id"]))
        markup.add(btn)

    if offset != 0:
        prev_btn = types.InlineKeyboardButton(
            "⏪ Previous", callback_data="mispro_prev_page"
        )
    if len(data) == word_limit:
        next_btn = types.InlineKeyboardButton(
            "Next ⏩", callback_data="mispro_next_page"
        )
    if "prev_btn" in locals():
        markup.row(prev_btn, next_btn)
    elif "next_btn" in locals():
        markup.row(next_btn)

    return markup


@bot.message_handler()
def main(message):
    bot.send_message(
        chat_id=message.chat.id,
        text="Cannot understand you(",
    )


@bot.callback_query_handler(func=lambda callback: True)
def callback_page_handler(callback):
    # handle parasite words pagination
    global parasite_cur_offset
    if callback.data == "parasite_prev_page":
        parasite_cur_offset -= 1
        markup = parasite_words_markup(callback.message, parasite_cur_offset)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=callback.message.text,
            reply_markup=markup,
        )
    elif callback.data == "parasite_next_page":
        parasite_cur_offset += 1
        markup = parasite_words_markup(callback.message, parasite_cur_offset)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=callback.message.text,
            reply_markup=markup,
        )

    # handle mispronounced words pagination
    global mispronounced_cur_offset
    if callback.data == "mispro_prev_page":
        mispronounced_cur_offset -= 1
        markup = mispronounced_words_markup(callback.message, mispronounced_cur_offset)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=callback.message.text,
            reply_markup=markup,
        )
    elif callback.data == "mispro_next_page":
        mispronounced_cur_offset += 1
        markup = mispronounced_words_markup(callback.message, mispronounced_cur_offset)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=callback.message.text,
            reply_markup=markup,
        )

    # handle single word audio sending
    if callback.data.isdigit():
        word_id = callback.data
        audio = requests.get(
            f"http://duryssoile.nu.edu.kz/api/v1.0/audio/{str(word_id)}"
        )
        if audio.status_code != 200:
            bot.send_message(chat_id=callback.message.chat.id, text="Error!")
            return

        word = requests.get(
            f"http://duryssoile.nu.edu.kz/api/v1.0/words/{str(word_id)}"
        )
        if word.status_code != 200:
            bot.send_message(chat_id=callback.message.chat.id, text="Error!")
            return

        global last_audio_id
        if last_audio_id != None:
            bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=last_audio_id,
            )

        word_name = json.loads(word.text)["word"]
        last_sent_audio = bot.send_voice(
            chat_id=callback.message.chat.id,
            voice=audio.content,
            caption=word_name,
        )
        last_audio_id = last_sent_audio.message_id


if __name__ == "__main__":
    bot.polling(non_stop=True)
