# libraries
import requests
import json
import telebot
from telebot import types

# local imports
import config

word_limit = 5
parasite_cur_offset = 1
mispronounced_cur_offset = 1

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
    # markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    # btn1 = types.KeyboardButton("List of words")
    # btn2 = types.KeyboardButton("Get one word")
    # btn3 = types.KeyboardButton("test")
    # markup.add(btn1, btn2, btn3)
    bot.send_message(
        chat_id=message.chat.id,
        text=f"Hello, {message.from_user.first_name}!",
        # reply_markup=markup,
    )


@bot.message_handler(commands=["parasite_words"])
def list_parasite_words(message):
    parasite_cur_offset = 1
    parasite_words_helper(parasite_cur_offset, message)


def parasite_words_helper(offset, message):
    parasite_words = requests.get(
        f"http://duryssoile.nu.edu.kz/api/v1.0/words?type=parasite&offset={offset}&limit={word_limit}&sort=asc"
    )
    if parasite_words.status_code != 200:
        bot.send_message(
            message.chat.id, f"Error! {parasite_words.status_code} Status Code recieved"
        )
        return

    markup = types.InlineKeyboardMarkup(row_width=2)

    for word in json.loads(parasite_words.text):
        btn = types.InlineKeyboardButton(word["word"], callback_data=word["id"])
        markup.add(btn)

    if offset != 1:
        prev_btn = types.InlineKeyboardButton(
            "⏪ Previous", callback_data="parasite_prev_page"
        )
    next_btn = types.InlineKeyboardButton("Next ⏩", callback_data="parasite_next_page")
    if "prev_btn" in locals():
        markup.row(prev_btn, next_btn)
    else:
        markup.row(next_btn)

    bot.send_message(message.chat.id, "List of words:", reply_markup=markup)


@bot.message_handler(commands=["mispronounced_words"])
def list_mispronounced_words(message):
    mispronounced_cur_offset = 1
    mispronounced_words_helper(mispronounced_cur_offset, message)


def mispronounced_words_helper(offset, message):
    misspronounced_words = requests.get(
        f"http://duryssoile.nu.edu.kz/api/v1.0/words?type=commonly-mispronounced&offset={offset}&limit={word_limit}&sort=asc"
    )
    if misspronounced_words.status_code != 200:
        bot.send_message(
            message.chat.id,
            f"Error! {misspronounced_words.status_code} Status Code recieved",
        )
        return

    markup = types.InlineKeyboardMarkup(row_width=2)

    for word in json.loads(misspronounced_words.text):
        btn = types.InlineKeyboardButton(word["word"], callback_data=word["id"])
        markup.add(btn)

    if offset != 1:
        prev_btn = types.InlineKeyboardButton(
            "⏪ Previous", callback_data="misspro_prev_page"
        )
    next_btn = types.InlineKeyboardButton("Next ⏩", callback_data="misspro_next_page")
    if "prev_btn" in locals():
        markup.row(prev_btn, next_btn)
    else:
        markup.row(next_btn)

    bot.send_message(message.chat.id, "List of words:", reply_markup=markup)


"""
@bot.message_handler(content_types=["text"])
def main(message):
    result = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={config.WEATHER_API}&units=metric"
    )
    if result.status_code == 200:
        data = json.loads(result.text)
        temp = data["main"]["temp"]
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Temperature in city {message.text} is {data}",
        )
    else:
        bot.send_message(chat_id=message.chat.id, text="Error occured")
"""


@bot.message_handler()
def main(message):
    bot.send_message(chat_id=message.chat.id, text="Cannot understand you(")


@bot.callback_query_handler(func=lambda callback: True)
def callback_page_handler(callback):
    global parasite_cur_offset
    if callback.data == "parasite_prev_page":
        parasite_cur_offset -= 1
        bot.delete_message(
            chat_id=callback.message.chat.id, message_id=callback.message.message_id
        )
        parasite_words_helper(parasite_cur_offset, callback.message)
    elif callback.data == "parasite_next_page":
        # bot.send_message(callback.message.chat.id, callback.message)
        parasite_cur_offset += 1
        bot.delete_message(
            chat_id=callback.message.chat.id, message_id=callback.message.message_id
        )
        parasite_words_helper(parasite_cur_offset, callback.message)
        # bot.edit_message_text(repl)

    global mispronounced_cur_offset
    if callback.data == "misspro_prev_page":
        mispronounced_cur_offset -= 1
        bot.delete_message(
            chat_id=callback.message.chat.id, message_id=callback.message.message_id
        )
        mispronounced_words_helper(mispronounced_cur_offset, callback.message)
    elif callback.data == "misspro_next_page":
        mispronounced_cur_offset += 1
        bot.delete_message(
            chat_id=callback.message.chat.id, message_id=callback.message.message_id
        )
        mispronounced_words_helper(mispronounced_cur_offset, callback.message)


if __name__ == "__main__":
    bot.polling(non_stop=True)

# bot.reply_to(message=callback.message, text="next page")
# bot.register_next_step_handler(callback.message, list_parasite_words)
