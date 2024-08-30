# libraries
import requests
import json
import telebot
from telebot import types
from dotenv import load_dotenv
import os

word_limit = 10
parasite_cur_offset = 0
# parasite_filter_offset = 0
mispronounced_cur_offset = 0
# mispronounced_filter_offset = 0
last_audio_id = None
filter = None

load_dotenv()
bot = telebot.TeleBot(os.getenv("TOKEN"))


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        chat_id=message.chat.id,
        text=f"Сәлем, {message.from_user.first_name}!",
    )


@bot.message_handler(commands=["parasite_words"])
def list_parasite_words(message):
    global filter
    global parasite_cur_offset
    filter = message.text.split()[1:]  # storing user args passed with the command
    filter = " ".join(filter)
    parasite_cur_offset = 0  # bug: if we go back to previous messages and press btns, it will crash because of the same offset
    # solution: can create different 4 offsets for filter and general list eetc. or can just delete prev

    parasite_markup = parasite_words_markup(message, parasite_cur_offset, filter)
    if parasite_markup != None:
        bot.send_message(
            chat_id=message.chat.id,
            text="Бөгде тіл сөздер:",
            reply_markup=parasite_markup,
        )


def parasite_words_markup(message, offset, filter):
    if len(filter) == 0:
        parasite_words = requests.get(
            f"http://duryssoile.nu.edu.kz/api/v1.0/words?type=parasite&offset={offset}&limit={word_limit}&sort=asc"
        )
    else:
        parasite_words = requests.get(
            f"http://duryssoile.nu.edu.kz/api/v1.0/words?type=parasite&filter={filter}&offset={offset}&limit={word_limit}&sort=asc"
        )

    if parasite_words.status_code != 200:
        bot.send_message(
            message.chat.id,
            f"Error! {parasite_words.status_code} Status Code received",
        )
        return None

    data = json.loads(parasite_words.text)
    # print(len(data))
    if len(data) == 0:
        bot.send_message(
            message.chat.id,
            "No such word exists",
        )
        return None

    markup = types.InlineKeyboardMarkup(row_width=2)

    for word in data:
        btn = types.InlineKeyboardButton(word["word"], callback_data=str(word["id"]))
        markup.add(btn)

    if offset != 0:
        prev_btn = types.InlineKeyboardButton(
            "⏪ Артқа", callback_data="parasite_prev_page"
        )
    if len(data) == word_limit:
        if len(filter) == 0:
            check_request = requests.get(
                f"http://duryssoile.nu.edu.kz/api/v1.0/words?type=parasite&offset={offset+1}&limit={word_limit}&sort=asc"
            )
        else:
            check_request = requests.get(
                f"http://duryssoile.nu.edu.kz/api/v1.0/words?type=parasite&filter={filter}&offset={offset+1}&limit={word_limit}&sort=asc"
            )
        # print(len(json.loads(check_request.text)))
        if len(json.loads(check_request.text)) != 0:
            next_btn = types.InlineKeyboardButton(
                "Келесі ⏩", callback_data="parasite_next_page"
            )
    if "prev_btn" in locals() and "next_btn" in locals():
        markup.row(prev_btn, next_btn)
    elif "prev_btn" in locals() and "next_btn" not in locals():
        markup.row(prev_btn)
    elif "next_btn" in locals() and "prev_btn" not in locals():
        markup.row(next_btn)

    return markup


@bot.message_handler(commands=["mispronounced_words"])
def list_mispronounced_words(message):
    global filter
    global mispronounced_cur_offset
    filter = message.text.split()[1:]  # storing user args passed with the command
    filter = " ".join(filter)
    mispronounced_cur_offset = 0

    markup = mispronounced_words_markup(message, mispronounced_cur_offset, filter)
    if markup != None:
        bot.send_message(
            chat_id=message.chat.id,
            text="Жиі қолданылатын сөздер:",
            reply_markup=markup,
        )


def mispronounced_words_markup(message, offset, filter):
    if len(filter) == 0:
        misspronounced_words = requests.get(
            f"http://duryssoile.nu.edu.kz/api/v1.0/words?type=commonly-mispronounced&offset={offset}&limit={word_limit}&sort=asc"
        )
    else:
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
    # print(len(data))
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
            "⏪ Артқа", callback_data="mispro_prev_page"
        )
    if len(data) == word_limit:
        if len(filter) == 0:
            check_request = requests.get(
                f"http://duryssoile.nu.edu.kz/api/v1.0/words?type=commonly-mispronounced&offset={offset+1}&limit={word_limit}&sort=asc"
            )
        else:
            check_request = requests.get(
                f"http://duryssoile.nu.edu.kz/api/v1.0/words?type=commonly-mispronounced&filter={filter}&offset={offset+1}&limit={word_limit}&sort=asc"
            )
        if len(json.loads(check_request.text)) != 0:
            next_btn = types.InlineKeyboardButton(
                "Келесі ⏩", callback_data="mispro_next_page"
            )
    if "prev_btn" in locals() and "next_btn" in locals():
        markup.row(prev_btn, next_btn)
    elif "prev_btn" in locals() and "next_btn" not in locals():
        markup.row(prev_btn)
    elif "next_btn" in locals() and "prev_btn" not in locals():
        markup.row(next_btn)

    return markup


@bot.message_handler()
def main(message):
    bot.send_message(
        chat_id=message.chat.id,
        text="Сізді түсінбедім(",
    )


@bot.callback_query_handler(func=lambda callback: True)
def callback_page_handler(callback):
    # handle parasite words pagination
    global parasite_cur_offset
    global filter
    # global last_parasite_id
    # if last_parasite_id != None:
    #     bot.delete_message(
    #         chat_id=callback.message.chat.id,
    #         message_id=last_parasite_id,
    #     )
    if callback.data == "parasite_prev_page":
        parasite_cur_offset -= 1
        markup = parasite_words_markup(callback.message, parasite_cur_offset, filter)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=callback.message.text,
            reply_markup=markup,
        )
    elif callback.data == "parasite_next_page":
        parasite_cur_offset += 1
        markup = parasite_words_markup(callback.message, parasite_cur_offset, filter)
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=callback.message.text,
            reply_markup=markup,
        )
    # last_parasite_id = callback.message.message_id

    # handle mispronounced words pagination
    global mispronounced_cur_offset
    # global last_mispro_id
    # if last_mispro_id != None:
    #     bot.delete_message(
    #         chat_id=callback.message.chat.id,
    #         message_id=last_mispro_id,
    #     )
    if callback.data == "mispro_prev_page":
        mispronounced_cur_offset -= 1
        markup = mispronounced_words_markup(
            callback.message, mispronounced_cur_offset, filter
        )
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=callback.message.text,
            reply_markup=markup,
        )
    elif callback.data == "mispro_next_page":
        mispronounced_cur_offset += 1
        markup = mispronounced_words_markup(
            callback.message, mispronounced_cur_offset, filter
        )
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=callback.message.text,
            reply_markup=markup,
        )
    # last_mispro_id = callback.message.message_id

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
        if last_audio_id:
            bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=last_audio_id,
            )

        word_data = json.loads(word.text)
        if int(callback.data) < 186:
            correct_version = word_data["correctVersions"][0]
            audio_text = (
                "❌" + word_data["word"] + "\n" + "✅" + correct_version["word"] + "\n\n"
            )
            audio_text += (
                "❌" + correct_version["incorrectUsage"] + "\n"
                "✅" + correct_version["correctUsage"]
            )

        else:
            audio_text = "🎧 " + word_data["word"]

        last_sent_audio = bot.send_voice(
            chat_id=callback.message.chat.id,
            voice=audio.content,
            caption=audio_text,
            )
        last_audio_id = last_sent_audio.message_id


if __name__ == "__main__":
    bot.polling(non_stop=True)
