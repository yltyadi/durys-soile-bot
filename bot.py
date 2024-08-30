import os
import asyncio
import tempfile 
import requests
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.fsm.storage.memory import MemoryStorage

load_dotenv()
TOKEN = os.getenv("TOKEN")

word_limit = 10
parasite_cur_offset = 0
mispronounced_cur_offset = 0
last_audio_id = None
filter_text = None

# Initialize bot, storage, dispatcher, and router
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# COMMAND HANDLERS
@router.message(Command("start"))
async def start(message: Message):
    await message.answer(f"Сәлем, {message.from_user.first_name}!")

@router.message(Command("parasite_words"))
async def list_parasite_words(message: Message):
    global parasite_cur_offset, filter_text
    filter_text = " ".join(message.text.split()[1:])
    parasite_cur_offset = 0

    parasite_markup = await parasite_words_markup(parasite_cur_offset, filter_text)
    if parasite_markup:
        await message.answer("Бөгде тіл сөздер:", reply_markup=parasite_markup)

async def parasite_words_markup(offset, filter_text):
    url = f"http://duryssoile.nu.edu.kz/api/v1.0/words?type=parasite&offset={offset}&limit={word_limit}&sort=asc"
    if filter_text:
        url += f"&filter={filter_text}"

    parasite_words = requests.get(url)

    if parasite_words.status_code != 200:
        return None

    data = parasite_words.json()
    if not data:
        return None

    buttons = []
    for word in data:
        buttons.append([InlineKeyboardButton(text=word["word"], callback_data=str(word["id"]))])

    if offset > 0 and len(data) == word_limit:
        buttons.append([InlineKeyboardButton(text="⏪ Артқа", callback_data="parasite_prev_page"),
                        InlineKeyboardButton(text="Келесі ⏩", callback_data="parasite_next_page")])
    elif offset > 0:
        buttons.append([InlineKeyboardButton(text="⏪ Артқа", callback_data="parasite_prev_page")])
    elif len(data) == word_limit:
         buttons.append([InlineKeyboardButton(text="Келесі ⏩", callback_data="parasite_next_page")])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup

@router.message(Command("mispronounced_words"))
async def list_mispronounced_words(message: Message):
    global mispronounced_cur_offset, filter_text
    filter_text = " ".join(message.text.split()[1:])
    mispronounced_cur_offset = 0

    mispro_markup = await mispronounced_words_markup(mispronounced_cur_offset, filter_text)
    if mispro_markup:
        await message.answer("Жиі қолданылатын сөздер:", reply_markup=mispro_markup)

async def mispronounced_words_markup(offset, filter_text):
    url = f"http://duryssoile.nu.edu.kz/api/v1.0/words?type=commonly-mispronounced&offset={offset}&limit={word_limit}&sort=asc"
    if filter_text:
        url += f"&filter={filter_text}"

    mispronounced_words = requests.get(url)

    if mispronounced_words.status_code != 200:
        return None

    data = mispronounced_words.json()
    if not data:
        return None
    
    buttons = []
    for word in data:
        buttons.append([InlineKeyboardButton(text=word["word"], callback_data=str(word["id"]))])

    if offset > 0 and len(data) == word_limit:
        buttons.append([InlineKeyboardButton(text="⏪ Артқа", callback_data="mispro_prev_page"),
                        InlineKeyboardButton(text="Келесі ⏩", callback_data="mispro_next_page")])
    elif offset > 0:
        buttons.append([InlineKeyboardButton(text="⏪ Артқа", callback_data="mispro_prev_page")])
    elif len(data) == word_limit:
         buttons.append([InlineKeyboardButton(text="Келесі ⏩", callback_data="mispro_next_page")])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


# DEFAULT MESSAGE HANDLER
@router.message()
async def default_handler(message: Message):
    await message.answer("Сізді түсінбедім(")


# CALLBACK QUERY HANDLERS
@router.callback_query(F.data == "parasite_prev_page")
async def parasite_prev_page(callback: CallbackQuery):
    global parasite_cur_offset, filter_text
    parasite_cur_offset -= 1
    markup = await parasite_words_markup(parasite_cur_offset, filter_text)
    await callback.message.edit_text("Бөгде тіл сөздер:", reply_markup=markup)

@router.callback_query(F.data == "parasite_next_page")
async def parasite_prev_page(callback: CallbackQuery):
    global parasite_cur_offset, filter_text
    parasite_cur_offset += 1
    markup = await parasite_words_markup(parasite_cur_offset, filter_text)
    await callback.message.edit_text("Бөгде тіл сөздер:", reply_markup=markup)

@router.callback_query(F.data == "mispro_prev_page")
async def parasite_prev_page(callback: CallbackQuery):
    global mispronounced_cur_offset, filter_text
    mispronounced_cur_offset -= 1
    markup = await mispronounced_words_markup(mispronounced_cur_offset, filter_text)
    await callback.message.edit_text("Жиі қолданылатын сөздер:", reply_markup=markup)

@router.callback_query(F.data == "mispro_next_page")
async def parasite_prev_page(callback: CallbackQuery):
    global mispronounced_cur_offset, filter_text
    mispronounced_cur_offset += 1
    markup = await mispronounced_words_markup(mispronounced_cur_offset, filter_text)
    await callback.message.edit_text("Жиі қолданылатын сөздер:", reply_markup=markup)

@router.callback_query(F.data.isdigit())
async def parasite_prev_page(callback: CallbackQuery):
    global last_audio_id
    word_id = callback.data
    audio = requests.get(f"http://duryssoile.nu.edu.kz/api/v1.0/audio/{word_id}")
    if audio.status_code != 200:
        await callback.message.answer("Error!")
        return

    word = requests.get(f"http://duryssoile.nu.edu.kz/api/v1.0/words/{word_id}")
    if word.status_code != 200:
        await callback.message.answer("Error!")
        return

    word_data = word.json()
    if int(callback.data) < 186:
        correct_version = word_data["correctVersions"][0]
        audio_text = (
            f"❌ {word_data['word']}\n✅ {correct_version['word']}\n\n"
            f"❌ {correct_version['incorrectUsage']}\n"
            f"✅ {correct_version['correctUsage']}"
        )
    else:
        audio_text = f"🎧 {word_data['word']}"

    if last_audio_id:
        await bot.delete_message(callback.message.chat.id, last_audio_id)

    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        temp_file.write(audio.content)
        temp_file.seek(0)
        audio_file = FSInputFile(temp_file.name)
        sent_audio = await bot.send_voice(chat_id=callback.message.chat.id, 
                                        voice=audio_file, 
                                        caption=audio_text)
        last_audio_id = sent_audio.message_id
        

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("bot has been stopped from terminal")
